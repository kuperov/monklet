import io
import zipfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse

from .models import Project, Interview, Question, Bot, ConsentLetter, MemberInvitation
from .forms import (
    ExportInterviewsForm,
    LundSurveyForm,
    ProjectForm,
    MemberInvitationForm,
    PublicConsentForm,
    QuestionForm,
    BotForm,
    ConsentLetterForm,
    InterviewForm,
    ManualTranscriptForm,
    InvitationResponseForm,
    InterviewConsentForm,
)
from apps.context_helpers import backend_context, blank_context
from apps.projects.util import datetime_str


def menu(project: Project):
    menu = [
        {
            "url": reverse_lazy("users:profile"),
            "icon": "menu-icon tf-icons ri-home-line",
            "name": "Home",
        }
    ]
    if project:
        menu += [
            {"menu_header": "Current project"},
            {
                "url": project.url,
                "icon": "menu-icon tf-icons ri-dashboard-line",
                "name": "Dashboard",
            },
            {
                "url": project.settings_url,
                "icon": "menu-icon tf-icons ri-settings-2-line",
                "name": "Project settings",
            },
            {
                "url": project.members_url,
                "icon": "menu-icon tf-icons ri-group-3-line",
                "name": "Members",
            },
            {"menu_header": "Interview design"},
            {
                "url": project.questions_url,
                "icon": "menu-icon tf-icons ri-question-line",
                "name": "Questions",
            },
            {
                "url": project.bots_url,
                "icon": "menu-icon tf-icons ri-robot-2-line",
                "name": "Bots",
            },
            {
                "url": project.consent_letters_url,
                "icon": "menu-icon tf-icons ri-heart-3-line",
                "name": "Consent letters",
            },
            {"menu_header": "Analysis"},
            {
                "url": reverse_lazy("project-responses", kwargs={"pk": project.pk}),
                "icon": "menu-icon tf-icons ri-message-line",
                "name": "Data",
            },
            {
                "url": reverse_lazy(
                    "project-interviews-list", kwargs={"pk": project.pk}
                ),
                "icon": "menu-icon tf-icons ri-chat-2-line",
                "name": "Interviews",
            },
            {
                "url": project.analysis_url,
                "icon": "menu-icon tf-icons ri-bar-chart-box-line",
                "name": "Harmonized analysis",
            },
        ]
    return {"menu": menu}


@login_required
# @permission_required('projects.view', raise_exception=True)
def project(request: HttpRequest, pk: str) -> HttpResponse:
    proj = get_object_or_404(Project, pk=pk)
    if not proj.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    inv_only = proj.interviews.filter(is_test=False, status="invited").count()
    started = proj.interviews.filter(
        is_test=False, has_consented=True, status="started"
    ).count()
    complete = proj.interviews.filter(
        is_test=False, has_consented=True, status="complete"
    ).count()
    followup_ok = (
        proj.interviews.filter(is_test=False, followup_consented=True)
        .exclude(status="invited")
        .count()
    )
    test = proj.interviews.filter(is_test=True).count()
    ctx = backend_context(
        {
            "project": proj,
            "menu_data": menu(proj),
            "inv_only": inv_only,
            "started": started,
            "complete": complete,
            "followup_ok": followup_ok,
            "test": test,
        }
    )
    return render(request, "projects/project.html", ctx)


@login_required
def project_settings(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.owner == request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project updated successfully")
            return redirect(project.url)
    else:
        form = ProjectForm(instance=project)
    ctx = backend_context(
        {"form": form, "project": project, "menu_data": menu(project=project)}
    )
    return render(request, "projects/detail.html", ctx)


@login_required
def project_new(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            proj = form.save()
            return redirect(reverse_lazy("project-members", kwargs={"pk": proj.id}))
    else:
        form = ProjectForm()
        form.helper.form_acount = reverse_lazy("project-new")
    ctx = backend_context({"form": form, "menu_data": menu(project=None)})
    return render(request, "projects/detail.html", ctx)


@login_required
def project_delete(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        project.deleted_at = now
        project.save()
        messages.success(request, "Project {project.name} deleted.")
        return redirect("profile")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "projects/delete.html", ctx)


@login_required
def project_leave(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user) or project.owner == request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        project.members.remove(request.user)
        project.save()
        messages.success(request, f"You have been removed from {project.name}.")
        return redirect("profile")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "projects/leave.html", ctx)


@login_required
def project_members(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "members/list.html", ctx)


@login_required
def project_analysis(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "analysis/summary.html", ctx)


@login_required
def project_questions(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "questions/list.html", ctx)


@login_required
def project_questions_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid:
            q = form.save(commit=False)
            q.project = project
            q.order = 1 + project.questions.count()
            q.save()
            messages.add_message(request, messages.SUCCESS, "Question added")
            return redirect("project-questions", pk=project.pk)
    else:
        form = QuestionForm()
    ctx = backend_context(
        {"form": form, "project": project, "menu_data": menu(project)}
    )
    return render(request, "questions/detail.html", ctx)


@login_required
def question_edit(request: HttpRequest, pk: str) -> HttpResponse:
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated question")
            return redirect("project-questions", pk=question.project.pk)
    else:
        form = QuestionForm(instance=question)
    ctx = backend_context({"form": form, "menu_data": menu(question.project)})
    return render(request, "questions/detail.html", ctx)


@login_required
def question_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    question = get_object_or_404(Question, pk=pk)
    project_id = question.project.pk
    question.delete()
    return redirect("project-questions", pk=project_id)


@login_required
def project_files(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "projects/files.html", ctx)


@login_required
def project_invite(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = MemberInvitationForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.project = project
            inv.send_email(request)  # saves
            messages.success(request, "Invitation sent")
            return redirect(project.members_url)
    else:
        form = MemberInvitationForm()
    ctx = backend_context(
        {"form": form, "project": project, "menu_data": menu(project)}
    )
    return render(request, "members/invite.html", ctx)


@login_required
def project_resend_invitation(request: HttpRequest, pk: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=pk)
    project = inv.project
    if not project.can_edit(request.user) or inv.accepted_email:
        raise PermissionDenied("User action not permitted.")
    inv.resend_email(request)
    return redirect("project-members", pk=project.pk)


@login_required
def project_cancel_invitation(request: HttpRequest, pk: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=pk)
    project = inv.project
    if not project.can_edit(request.user) or inv.accepted_email:
        raise PermissionDenied("User action not permitted.")
    inv.expire()
    return redirect("project-members", pk=project.pk)


@login_required
def project_bots(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context(
        {
            "project": project,
            "menu_data": menu(project),
            "bots": project.bots.filter(deleted_at=None),
        }
    )
    return render(request, "bots/list.html", ctx)


@login_required
def project_bots_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = BotForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.project = project
            b.save()
            messages.add_message(request, messages.SUCCESS, "Bot added")
            return redirect("project-bots", pk=project.pk)
    else:
        form = BotForm()
    ctx = backend_context(
        {"form": form, "project": project, "menu_data": menu(project)}
    )
    return render(request, "bots/detail.html", ctx)


@login_required
def bot_edit(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    if request.method == "POST":
        form = BotForm(request.POST, instance=bot)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated bot")
            return redirect("project-bots", pk=bot.project.pk)
    else:
        form = BotForm(instance=bot)
    ctx = backend_context({"form": form, "menu_data": menu(bot.project)})
    return render(request, "bots/detail.html", ctx)


@login_required
def bot_delete(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    project_id = bot.project.pk
    bot.deleted_at = now()
    bot.save()
    messages.success(request, "Bot deleted")
    return redirect("project-bots", pk=project_id)


# note no login required
def bot_public(request: HttpRequest, pk: str) -> HttpResponse:
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
    ctx = blank_context(
        {
            "bot": bot,
            "project": project,
            "form": form,
            "ip_address": request.headers.get("X-Real-IP"),
            "is_collaborator": is_collaborator,
        }
    )
    return render(request, "interviews/public.html", ctx)


@login_required
def bot_duplicate(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    if not bot.project.can_edit(request.user):
        return redirect("users:profile")
    bot.pk = None
    prefix = "Copy of "
    for i in range(100):
        if Bot.objects.filter(name=prefix + bot.name).exists():
            prefix = prefix + "copy of "
    bot.name = prefix + bot.name
    bot.save()
    return redirect("project-bots", pk=bot.project.pk)


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
    ctx = blank_context({"interview": interview, "form": form})
    return render(request, "interviews/lund_questions.html", ctx)


@login_required
def project_simulate(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    interview = None
    if request.GET.get("bot"):
        bot = get_object_or_404(Bot, pk=request.GET["bot"])
        if bot.project.pk != project.pk:
            raise PermissionDenied("Invalid bot code")
        interview = Interview.objects.create(
            project=project,
            bot=bot,
            subject_name=request.user.name,
            subject_email=request.user.email,
            is_test=True,
            status="invited",
        )
    ctx = backend_context(
        {
            "project": project,
            "bots": project.enabled_bots(),
            "test_interviews": project.test_interviews(),
            "menu_data": menu(project),
        }
    )
    if interview:
        ctx["initial_interview"] = interview.pk
    return render(request, "bots/simulator.html", ctx)


@login_required
def test_interviews_json(request: HttpRequest, pk: str) -> JsonResponse:
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
def interview_messages(request: HttpRequest, pk: str) -> JsonResponse:
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


# note: unauthenticated view - interview_code provides security
def interview(request, interview_code):
    iv = get_object_or_404(Interview, pk=interview_code)
    ctx = blank_context({"project": iv.project, "interview": iv})
    return render(
        request,
        "interviews/interview.html",
        ctx,
    )


@login_required
def interview_delete(request, pk):
    iv = get_object_or_404(Interview, pk=pk)
    if not iv.project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    iv.deleted_at = now()
    iv.save()
    next = request.GET.get(
        "next", reverse_lazy("project-responses", kwargs={"pk": iv.project.id})
    )
    return redirect(next)


# unauthenticated view
def interview_landing(request, pk):
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
    ctx = blank_context(
        {
            "form": form,
            "project": project,
            "bot": iv.bot,
            "interview": iv,
            "is_collaborator": project.can_view(request.user),
        }
    )
    return render(request, "interviews/landing.html", ctx)


@login_required
def interview_conversation(request, pk):
    iv = get_object_or_404(Interview, pk=pk)
    msg_list = iv.messages_list()
    prompt_tokens, gen_tokens, total_tokens = iv.total_token_usage()
    ctx = backend_context(
        {
            "interview": iv,
            "project": iv.project,
            "msg_list": msg_list,
            "menu_data": menu(iv.project),
            "prompt_tokens": prompt_tokens,
            "gen_tokens": gen_tokens,
            "total_tokens": total_tokens,
        }
    )
    return render(request, "interviews/conversation.html", ctx)


@login_required
def project_consent_letters(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "consent_letters/list.html", ctx)


@login_required
def project_consent_letters_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ConsentLetterForm(request.POST)
        if form.is_valid:
            let = form.save(commit=False)
            let.project = project
            let.save()
            messages.add_message(request, messages.SUCCESS, "Consent letter added")
            return redirect("project-consent-letters", pk=project.pk)
    else:
        form = ConsentLetterForm()
    ctx = backend_context(
        {"form": form, "project": project, "menu_data": menu(project)}
    )
    return render(request, "consent_letters/detail.html", ctx)


@login_required
def consent_letter_edit(request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    if request.method == "POST":
        form = ConsentLetterForm(request.POST, instance=consent_letter)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated consent_letter")
            return redirect("project-consent-letters", pk=consent_letter.project.pk)
    else:
        form = ConsentLetterForm(instance=consent_letter)
    ctx = backend_context({"form": form, "menu_data": menu(consent_letter.project)})
    return render(request, "consent_letters/detail.html", ctx)


def consent_letter_public(request: HttpRequest, pk: str) -> HttpRequest:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    ctx = blank_context({"project": consent_letter.project, "letter": consent_letter})
    return render(request, "consent_letters/public.html", ctx)


@login_required
def consent_letter_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    project_id = consent_letter.project.pk
    consent_letter.delete()
    return redirect("project-consent-letters", pk=project_id)


@login_required
def project_interviews_invited(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    interviews = project.interviews.filter(deleted_at=None, status="invited")
    ctx = backend_context(
        {"project": project, "interviews": interviews, "menu_data": menu(project)}
    )
    return render(request, "interviews/invited.html", ctx)


@login_required
def project_interviews_list(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context(
        {
            "project": project,
            "menu_data": menu(project),
            "invited_interviews": project.invited_interviews(),
            "interviews": project.started_completed_interviews(),
            "test_interviews": project.test_interviews(),
            "is_editor": project.can_edit(request.user),
        }
    )
    return render(request, "interviews/list.html", ctx)


@login_required
def projects_export_interviews(request: HttpRequest, pk: str) -> HttpResponse:
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
    ctx = backend_context({"form": form, "menu_data": menu(proj)})
    return render(request, "interviews/export.html", ctx)


@login_required
def project_interviews_invite(request: HttpRequest, pk: str) -> HttpResponse:
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
    ctx = backend_context(
        {"form": form, "project": project, "menu_data": menu(project)}
    )
    return render(request, "interviews/new.html", ctx)


@login_required
def project_transcripts(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project, "menu_data": menu(project)})
    return render(request, "transcripts/list.html", ctx)


@login_required
def project_transcripts_upload(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ManualTranscriptForm(request.POST)
        if form.is_valid:
            ts = form.save(commit=False)
            ts.project = project
            ts.save()
            messages.add_message(request, messages.SUCCESS, "Transcript added")
            return redirect("project-transcripts", pk=project.pk)
    else:
        form = ManualTranscriptForm()
    ctx = backend_context({"form": form, "menu_data": menu(project)})
    return render(request, "transcripts/upload.html", ctx)


# at this point users are possibly unauthenticated
def invitation_landing(request: HttpRequest, code: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=code)
    if request.user == inv.project.owner:  # owner clicked own link
        return redirect(inv.project.url)
    if not inv.is_valid:
        ctx = blank_context({"unavailable": True})
    elif not request.user.is_authenticated:
        ctx = blank_context({"project": inv.project, "return_url": inv.landing_url})
    else:
        # logged in, so just ask if accept
        form = InvitationResponseForm()
        form.helper.form_action = reverse_lazy(
            "invitation-respond", kwargs={"code": code}
        )
        ctx = blank_context({"form": form})
    return render(request, "invitations/landing.html", ctx)


def invitation_respond(request: HttpRequest, code: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=code)
    if not inv.is_valid:
        return render(request, "invitations/not_available.html")
    if request.user == inv.project.owner:  # owner clicked own link
        return redirect(inv.project.url)
    if not request.user.is_authenticated:
        return redirect(inv.landing_url)
    if request.method == "POST" and request.POST.get("yes"):
        inv.accept(request.user)
        inv.save()
        return redirect(inv.project.url)
    else:
        raise PermissionDenied("User action not permitted.")
