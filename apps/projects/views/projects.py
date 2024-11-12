from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.timezone import now
from apps.context_helpers import backend_context
from apps.projects.forms import ProjectForm
from apps.projects.models import Project


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


@login_required
# @permission_required('projects.view', raise_exception=True)
def dashboard(request: HttpRequest, pk: str) -> HttpResponse:
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
            "inv_only": inv_only,
            "started": started,
            "complete": complete,
            "followup_ok": followup_ok,
            "test": test,
        }
    )
    return render(request, "projects/project.html", ctx)


@login_required
def settings(request: HttpRequest, pk: str) -> HttpResponse:
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
        {"form": form, "project": project}
    )
    return render(request, "projects/detail.html", ctx)


@login_required
def new(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            proj = form.save()
            return redirect(reverse_lazy("project-members", kwargs={"pk": proj.id}))
    else:
        form = ProjectForm()
        form.helper.form_acount = reverse_lazy("project-new")
    ctx = backend_context({"form": form, "project": dashboard})
    return render(request, "projects/detail.html", ctx)


@login_required
def delete(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        project.deleted_at = now()
        project.save()
        messages.success(request, "Project {project.name} deleted.")
        return redirect("profile")
    ctx = backend_context({"project": project})
    return render(request, "projects/delete.html", ctx)


@login_required
def leave(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user) or project.owner == request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        project.members.remove(request.user)
        project.save()
        messages.success(request, f"You have been removed from {project.name}.")
        return redirect("profile")
    ctx = backend_context({"project": project})
    return render(request, "projects/leave.html", ctx)
