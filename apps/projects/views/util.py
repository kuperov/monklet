from apps.projects.models import Project


from django.core.exceptions import PermissionDenied
from django.http import HttpRequest
from django.shortcuts import get_object_or_404


def get_viewable_project(request: HttpRequest, pk: str) -> Project:
    """Get project identified by pk

    Args:
        request: current request
        pk: id of project

    Raises:
        PermissionDenied: if request.user can't view this project
        Http404: if project is not found
    """
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    return project


def get_editable_project(request: HttpRequest, pk: str) -> Project:
    """Get project identified by pk

    Args:
        request: current request
        pk: id of project

    Raises:
        PermissionDenied: if request.user can't edit this project
        Http404: if project is not found
    """
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    return project
