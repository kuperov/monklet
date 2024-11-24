from apps.projects import tasks
from apps.projects.models import Project


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from apps.projects.views.util import get_editable_project, get_viewable_project


@login_required
def themes(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk)
    return render(request, "analysis/themes.html", {"project": project})


@login_required
def regenerate_themes(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk)
    tasks.get_themes.delay(str(project.pk))
    messages.success(request, "Themes regenerating. Refresh the page in a few seconds.")
    return render(request, "analysis/_themes.html", {"project": project})


@login_required
def query(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {"project": project}
    return render(request, "analysis/query.html", ctx)


@login_required
def harmonized(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {"project": project}
    return render(request, "analysis/harmonized.html", ctx)
