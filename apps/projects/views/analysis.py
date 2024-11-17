from apps.projects.models import Project


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render


@login_required
def themes(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {"project": project}
    return render(request, "analysis/themes.html", ctx)


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
