import io
import zipfile

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.timezone import now
from apps.projects.forms import (
    ExportInterviewsForm,
    InterviewConsentForm,
    InterviewForm,
    LundSurveyForm,
    PublicConsentForm,
)
from apps.projects.models import Bot, Interview, Project


from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.projects.util import datetime_str


# note: unauthenticated view - interview_code provides security
def landing_invited(request, interview_code):
    iv = get_object_or_404(Interview, pk=interview_code)
    return render(
        request,
        "interviews/interview.html",
        {"project": iv.project, "interview": iv},
    )


# unauthenticated view
def uninvited_landing(request, pk):
    iv = get_object_or_404(Interview, pk=pk)
    project = iv.project
    interview_url = reverse_lazy("interview", kwargs={"interview_code": iv.pk})
    if iv.has_consented:
        return redirect(interview_url)
    if request.method == "POST":
        form = InterviewConsentForm(request.POST, instance=iv)
        if form.is_valid():
            iv = form.save()
            if iv.bot.config.get("show_lund_questions"):
                return redirect(reverse_lazy("lund-questions", kwargs=dict(pk=iv.pk)))
            else:
                return redirect(interview_url)
    else:
        form = InterviewConsentForm(instance=iv)
    ctx = {
        "form": form,
        "project": project,
        "bot": iv.bot,
        "interview": iv,
        "is_collaborator": project.can_view(request.user),
    }
    return render(request, "interviews/landing.html", ctx)


@login_required
def list_json(request: HttpRequest, pk: str) -> JsonResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")

    def format(iv: Interview):
        return {
            "interview": iv.pk,
            "names": f"{iv.bot.name} & {iv.subject_name}",
            "bot_name": iv.bot.name,
            "bot_version": iv.bot.version,
            "last_text": iv.last_message_text(),
            "updated_at": naturaltime(iv.updated_at),
            "status": iv.status,
        }

    data = [format(iv) for iv in project.test_interviews()]
    return JsonResponse(data, safe=False)  # safe=False serializes uuid and date


@login_required
def delete(request, pk):
    iv = get_object_or_404(Interview, pk=pk)
    if not iv.project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    iv.deleted_at = now()
    iv.save()
    next = request.GET.get(
        "next", reverse_lazy("project-responses", kwargs={"pk": iv.project.id})
    )
    return redirect(next)


@login_required
def conversation(request, pk):
    iv = get_object_or_404(Interview, pk=pk)
    msg_list = iv.messages_list()
    prompt_tokens, gen_tokens, total_tokens = iv.total_token_usage()
    ctx = {
        "interview": iv,
        "project": iv.project,
        "msg_list": msg_list,
        "prompt_tokens": prompt_tokens,
        "gen_tokens": gen_tokens,
        "total_tokens": total_tokens,
    }
    return render(request, "interviews/conversation.html", ctx)


@login_required
def list_invited(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    interviews = project.interviews.filter(deleted_at=None, status="invited")
    ctx = {"project": project, "interviews": interviews}
    return render(request, "interviews/invited.html", ctx)


@login_required
def list(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    interviews = project.started_completed_interviews()
    template = "interviews/list.html"
    if request.method == "POST":
        # nb default status is started/completed
        if request.POST.get("status") == "invited":
            interviews = project.invited_interviews()
        elif request.POST.get("status") == "test":
            interviews = project.test_interviews()
        if request.POST.get("followup") == "ok_only":
            interviews = interviews.filter(followup_consented=True)
        elif request.POST.get("followup") == "no_only":
            interviews = interviews.filter(followup_consented=False)
        if request.POST.get("bot", "all") != "all":
            interviews = interviews.filter(bot_id=request.POST.get("bot"))
        if request.headers.get("HX-Request") == "true":
            template = "interviews/_interview_table.html"
    ctx = {
        "project": project,
        "interviews": interviews,
        "is_editor": project.can_edit(request.user),
    }
    return render(request, template, ctx)


@login_required
def export(request: HttpRequest, pk: str) -> HttpResponse:
    proj = get_object_or_404(Project, pk=pk)
    if not proj.can_edit(request.user):
        raise PermissionDenied(
            "User must be an editor of the project to export interviews"
        )
    if request.method == "POST":
        form = ExportInterviewsForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["what"] == "interviews":
                interviews = proj.started_completed_interviews()
            elif form.cleaned_data["what"] == "test":
                interviews = proj.test_interviews()
            else:
                raise Exception("Invalid selection")
            include_metadata = form.cleaned_data["include_metadata"]
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_archive:
                for iv in interviews:
                    doc_buffer = io.BytesIO()
                    iv.as_docx(include_metadata=include_metadata).save(doc_buffer)
                    doc_buffer.seek(0)
                    fname = f"{iv.subject_name}-{iv.bot.name}.docx"
                    zip_archive.writestr(fname, doc_buffer.read())
            zip_buffer.seek(0)
            response = HttpResponse(zip_buffer, content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="interviews.zip"'
            return response
    else:
        form = ExportInterviewsForm()
    ctx = {"form": form, "project": proj}
    return render(request, "interviews/export.html", ctx)


@login_required
def invite(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = InterviewForm(request.POST)
        if form.is_valid:
            inv = form.save(commit=False)
            inv.project = project
            inv.status = "invited"
            inv.save()
            inv.send_invitation_email(request)
            messages.add_message(request, messages.SUCCESS, "Interview invitation sent")
            return redirect("project-invitations", pk=project.pk)
    else:
        form = InterviewForm()
        if "bot" in request.GET:
            form.initial["bot"] = request.GET["bot"]
    ctx = {"form": form, "project": project}
    return render(request, "interviews/new.html", ctx)


def lund_questions(request: HttpRequest, pk: str) -> HttpResponse:
    interview = get_object_or_404(Interview, pk=pk)
    if request.method == "POST":
        form = LundSurveyForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["is_academic"] != "no":
                is_student = form.cleaned_data["is_student"] != "no"
                if not form.cleaned_data["academic_age"] and not is_student:
                    form.add_error(
                        "academic_age",
                        "How many years since you received your academic qualification?",
                    )
                if not form.cleaned_data["discipline"]:
                    form.add_error(
                        "discipline", "Please specify your main academic discipline"
                    )
        if form.is_valid():
            attrs = {
                k: form.cleaned_data[k]
                for k in ["is_academic", "is_student", "academic_age", "discipline"]
            }
            interview.attributes.update(attrs)
            interview.save()
            return redirect("interview", interview_code=interview.pk)
    else:
        form = LundSurveyForm()
    ctx = {"interview": interview, "form": form}
    return render(request, "interviews/lund_questions.html", ctx)


@login_required
def messages_json(request: HttpRequest, pk: str) -> JsonResponse:
    interview = get_object_or_404(Interview, pk=pk)
    project = interview.project
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")

    def format(msg):
        return {
            "uuid": msg.get("uuid"),
            "sender": msg.get("sender"),
            "message": msg.get("message"),
            "sent_at": datetime_str(msg.get("sent_at")),
        }

    data = [format(msg) for msg in interview.content]
    return JsonResponse(data, safe=False)  # safe=False serializes uuid and date


def landing_public(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    if not bot.allow_public:
        raise PermissionDenied("Use of this bot is by invitation only.")
    project = bot.project
    is_collaborator = project.can_view(request.user)
    if request.method == "POST":
        form = PublicConsentForm(request.POST)
        form.is_valid()
        if (
            not form.cleaned_data["subject_email"]
            and form.cleaned_data["followup_consented"]
        ):
            form.add_error(
                "subject_email", "Please provide your email address for follow-up."
            )
        if form.is_valid():
            interview = form.save(commit=False)
            interview.project = project
            interview.bot = bot
            interview.ip_address = request.headers.get("X-Real-IP")
            interview.status = "invited"
            interview.is_test = is_collaborator  # user is logged in as a collaborator
            interview.save()
            # hack hack hack
            if bot.config.get("show_lund_questions"):
                return redirect(
                    reverse_lazy("lund-questions", kwargs=dict(pk=interview.pk))
                )
            interview_url = reverse_lazy(
                "interview", kwargs={"interview_code": interview.pk}
            )
            return redirect(interview_url)
    else:
        form = PublicConsentForm()
    ctx = {
        "bot": bot,
        "project": project,
        "form": form,
        "ip_address": request.headers.get("X-Real-IP"),
        "is_collaborator": is_collaborator,
    }
    return render(request, "interviews/public.html", ctx)
