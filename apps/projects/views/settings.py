from django.contrib import messages
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from apps.projects import forms
from apps.projects.models import MemberInvitation
from apps.projects.views.util import get_editable_project, get_viewable_project


# all settings tabs
@login_required
@require_GET
def view(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk=pk)
    form = forms.ProjectForm(instance=project)
    ctx = {"project": project, "form": form}
    return render(request, "settings/index.html", ctx)


@login_required
def settings_tab(request: HttpRequest, pk: str) -> HttpResponse:
    # always called by HTMX
    project = get_editable_project(request, pk=pk)
    if request.method == "POST":
        form = forms.ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project updated successfully")
            return render(request, "settings/_settings.html", {"project": project})
    else:
        form = forms.ProjectForm(instance=project)
    if request.GET.get("readonly") == "true":
        return render(request, "settings/_settings.html", {"project": project})
    else:
        return render(
            request, "settings/_edit_settings.html", {"form": form, "project": project}
        )


@login_required
def invite(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk=pk)
    if request.method == "POST":
        form = forms.MemberInvitationForm(request.POST)
        if form.is_valid():
            inv: MemberInvitation = form.save(commit=False)
            inv.project = project
            inv.send_email(request)  # saves
            messages.success(request, f"Invitation sent to {inv.email}")
            return render(request, "settings/_members.html", {"project": project})
    else:
        form = forms.MemberInvitationForm()
    if request.GET.get("cancel") == "true":
        return render(request, "settings/_members.html", {"project": project})
    else:
        ctx = {"form": form, "project": project}
        return render(request, "settings/_invite.html", ctx)


@login_required
def invitations(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk)
    return render(request, "settings/_invitations_sent.html", {"project": project})


@login_required
def resend_invitation(request: HttpRequest, pk: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=pk)
    project = inv.project
    if not project.can_edit(request.user) or inv.accepted_email:
        raise PermissionDenied("User action not permitted.")
    inv.resend_email(request)
    messages.success(request, f"Sent invitation to {inv.email}")
    return render(request, "settings/_invitations_sent.html", {"project": project})


@login_required
def cancel_invitation(request: HttpRequest, pk: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=pk)
    project = inv.project
    if not project.can_edit(request.user) or inv.accepted_email:
        raise PermissionDenied("User action not permitted.")
    inv.expire()
    return redirect("project-settings", pk=project.pk)


def invitation_respond(request: HttpRequest, code: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=code)
    if not inv.is_valid:
        return render(request, "invitations/not_available.html")
    if request.user == inv.project.owner:  # owner clicked own link
        return redirect(inv.project.get_absolute_url())
    if not request.user.is_authenticated:
        return redirect(inv.landing_url)
    if request.method == "POST" and request.POST.get("yes"):
        inv.accept(request.user)
        inv.save()
        return redirect(inv.project.get_absolute_url())
    else:
        raise PermissionDenied("User action not permitted.")


# at this point users are possibly unauthenticated
def invitation_landing(request: HttpRequest, code: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=code)
    if request.user == inv.project.owner:  # owner clicked own link
        return redirect(inv.project.get_absolute_url())
    if not inv.is_valid:
        ctx = {"unavailable": True}
    elif not request.user.is_authenticated:
        ctx = {"project": inv.project, "return_url": inv.landing_url}
    else:
        # logged in, so just ask if accept
        form = forms.InvitationResponseForm()
        form.helper.form_action = reverse_lazy(
            "invitation-respond", kwargs={"code": code}
        )
        ctx = {"form": form}
    return render(request, "invitations/landing.html", ctx)
