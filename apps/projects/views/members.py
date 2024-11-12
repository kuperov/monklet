from django.contrib import messages
from apps.context_helpers import backend_context, blank_context
from apps.projects import forms
from apps.projects.models import MemberInvitation, Project


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy


@login_required
def project_members(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project})
    return render(request, "members/list.html", ctx)


@login_required
def project_invite(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = forms.MemberInvitationForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.project = project
            inv.send_email(request)  # saves
            messages.success(request, "Invitation sent")
            return redirect(project.members_url)
    else:
        form = forms.MemberInvitationForm()
    ctx = backend_context(
        {"form": form, "project": project}
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
        form = forms.InvitationResponseForm()
        form.helper.form_action = reverse_lazy(
            "invitation-respond", kwargs={"code": code}
        )
        ctx = blank_context({"form": form})
    return render(request, "invitations/landing.html", ctx)
