from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.projects import models


@login_required
def index(request, pk):
    case = get_object_or_404(models.Case, pk=pk)
    project = case.project
    if not project.can_view(request.user):
        raise PermissionError("Operation not permitted")
    return render(request, "case/index.html", {"project": project, "case": case})
