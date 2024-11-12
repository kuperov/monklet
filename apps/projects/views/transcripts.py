from django.contrib import messages
from apps.context_helpers import backend_context
from apps.projects.forms import ManualTranscriptForm
from apps.projects.models import Project


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


@login_required
def project_transcripts(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project})
    return render(request, "transcripts/list.html", ctx)


@login_required
def project_transcripts_upload(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ManualTranscriptForm(request.POST)
        if form.is_valid:
            ts = form.save(commit=False)
            ts.project = project
            ts.save()
            messages.add_message(request, messages.SUCCESS, "Transcript added")
            return redirect("project-transcripts", pk=project.pk)
    else:
        form = ManualTranscriptForm()
    ctx = backend_context({"form": form, "project": project})
    return render(request, "transcripts/upload.html", ctx)
