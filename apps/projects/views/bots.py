from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.timezone import now
from apps.context_helpers import backend_context, blank_context
from apps.projects.forms import BotForm, PublicConsentForm
from apps.projects.models import Bot, Interview, Project


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render



@login_required
def list(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context(
        {
            "project": project,
            "bots": project.bots.filter(deleted_at=None),
        }
    )
    return render(request, "bots/list.html", ctx)


@login_required
def new(request: HttpRequest, pk: str) -> HttpResponse:
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
        {"form": form, "project": project}
    )
    return render(request, "bots/detail.html", ctx)


@login_required
def edit(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    if request.method == "POST":
        form = BotForm(request.POST, instance=bot)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated bot")
            return redirect("project-bots", pk=bot.project.pk)
    else:
        form = BotForm(instance=bot)
    ctx = backend_context({"form": form, "project": bot.project})
    return render(request, "bots/detail.html", ctx)


@login_required
def delete(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    project_id = bot.project.pk
    bot.deleted_at = now()
    bot.save()
    messages.success(request, "Bot deleted")
    return redirect("project-bots", pk=project_id)


# note no login required
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
def duplicate(request: HttpRequest, pk: str) -> HttpResponse:
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


@login_required
def simulate(request: HttpRequest, pk: str) -> HttpResponse:
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
        }
    )
    if interview:
        ctx["initial_interview"] = interview.pk
    return render(request, "bots/simulator.html", ctx)
