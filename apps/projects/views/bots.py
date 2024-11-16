from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.contrib import messages
from django.urls import reverse
from django.utils.timezone import now
from apps.projects import forms
from apps.projects.models import Bot, ConsentLetter, Interview, Project
from apps.projects.views.util import get_editable_project, get_viewable_project


@login_required
def index(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk)
    return render(request, "bots/index.html", {"project": project})


@login_required
def new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk=pk)
    if request.method == "POST":
        form = forms.BotForm(request.POST)
        if form.is_valid():
            b = form.save(commit=False)
            b.project = project
            b.save()
            messages.success(request, "Bot added")
            return render(request, "bots/_bots.html", {"project": project})
    else:
        form = forms.BotForm()
    if request.GET.get("cancel") == "true":
        return render(request, "bots/_bots.html", {"project": project})
    else:
        ctx = {"form": form, "project": project}
        return render(request, "bots/_new_bot.html", ctx)


@login_required
def edit(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    if not bot.project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = forms.BotForm(request.POST, instance=bot)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated bot")
            return render(request, "bots/_bots.html", {"project": bot.project})
    else:
        form = forms.BotForm(instance=bot)
    if request.GET.get("cancel") == "true":
        return render(request, "bots/_bots.html", {"project": bot.project})
    else:
        ctx = {"form": form, "project": bot.project}
        return render(request, "bots/_edit_bot.html", ctx)


@login_required
def delete(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    bot.deleted_at = now()
    bot.save()
    messages.success(request, "Bot deleted")
    return render(request, "bots/_bots.html", {"project": bot.project})


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
    ctx = {
        "project": project,
        "bots": project.enabled_bots(),
        "test_interviews": project.test_interviews(),
    }
    if interview:
        ctx["initial_interview"] = interview.pk
    return render(request, "bots/simulator.html", ctx)


@login_required
def delete_letter(request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    consent_letter.delete()
    return render(request, "bots/_letters.html", {"project": consent_letter.project})


@login_required
def edit_letter(request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    endpoint = reverse("consent-letter-edit", kwargs={"pk": consent_letter.pk})
    if request.method == "POST":
        form = forms.ConsentLetterForm(endpoint, request.POST, instance=consent_letter)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated consent_letter")
            return render(
                request, "bots/_letters.html", {"project": consent_letter.project}
            )
    else:
        form = forms.ConsentLetterForm(endpoint, instance=consent_letter)
    ctx = {"form": form, "project": consent_letter.project}
    return render(request, "bots/_letter_detail.html", ctx)


@login_required
def new_letter(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    endpoint = reverse("project-consent-letters-new", kwargs={"pk": project.pk})
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = forms.ConsentLetterForm(endpoint, request.POST)
        if form.is_valid:
            let = form.save(commit=False)
            let.project = project
            let.save()
            messages.add_message(request, messages.SUCCESS, "Consent letter added")
            return render(request, "bots/_letters.html", {"project": project})
    else:
        form = forms.ConsentLetterForm(endpoint)
    ctx = {"form": form, "project": project}
    return render(request, "bots/_letter_detail.html", ctx)


def view_letter(request: HttpRequest, pk: str) -> HttpRequest:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    ctx = {"project": consent_letter.project, "letter": consent_letter}
    return render(request, "bots/public_letter.html", ctx)
