from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, reverse

from apps.projects.views.util import get_viewable_project
from apps.users.models import User
from apps.projects import models


def all_cases(request: HttpRequest, pk: str) -> HttpResponse:
    if not all(h in request.headers for h in ["email", "token"]):
        raise PermissionDenied("Not authorized")
    user = User.objects.get(email=request.headers["email"])
    project = models.Project.objects.get(pk=pk)
    if not user or not project or not project.can_view(user):
        raise PermissionDenied("Not authorized")
    # user authorized
    data = []
    for case in project.current_cases():
        datum = []
        for record in case.current_records():
            datum.append({"record_type": record.record_type, "content": record.content})
        data.append(datum)
    return JsonResponse(data)


@login_required
def api_access_example(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk)
    api_url = request.build_absolute_uri(
        reverse("api-all-cases", kwargs={"pk": project.pk})
    )
    return render(
        request, "api/_python_example.html", {"project": project, "api_url": api_url}
    )
