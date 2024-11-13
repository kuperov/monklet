from django.contrib import messages
from apps.context_helpers import backend_context
from apps.projects import forms, models

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now

from apps.projects.views.util import get_editable_project


@login_required
def list(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(models.Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project})
    return render(request, "transcripts/list.html", ctx)


@login_required
def new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk=pk)
    if request.method == "POST":
        form = forms.ManualTranscriptForm(request.POST)
        if form.is_valid:
            ts = form.save(commit=False)
            ts.project = project
            ts.save()
            messages.add_message(request, messages.SUCCESS, "Transcript added")
            return redirect("project-transcripts", pk=project.pk)
    else:
        form = forms.ManualTranscriptForm()
    ctx = backend_context({"form": form, "project": project})
    return render(request, "transcripts/upload.html", ctx)



@login_required
def project_import_chats(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk)
    already_imported = set([t.interview_id for t in project.transcripts.all()])
    ivs = {iv.pk: iv for iv in project.started_completed_interviews() if iv.pk not in already_imported}
    if request.method == "POST":
        formset = forms.ImportChatFormSet(request.POST)
        if formset.is_valid():
            num_imported = sum([iv.cleaned_data["selected"] for iv in formset])
            if num_imported == 0:
                formset.errors.append("Please select at least one interview")
            else:
                for iv in formset:
                    if iv.cleaned_data["selected"]:
                        chat = models.Interview.objects.get(pk=iv.cleaned_data["id"])
                        if chat.project.id != project.id:
                            raise PermissionDenied("Invalid project")
                        ts = models.Transcript.from_chat(chat, pseudonym=iv.cleaned_data["pseudonym"])
                        ts.save()
                messages.success(request, f"Created {num_imported} transcripts")
                return redirect('project-responses', pk=project.pk)
    else:
        # list unimported interviews, come up with pseudonyms
        initial = [{"id": k, "pseudonym": iv.subject_name, "selected": False}
                   for k, iv in ivs.items()]
        formset = forms.ImportChatFormSet(initial=initial)

    # read-only fields not passed through in GET data
    for form, iv in zip(formset, ivs.values()):
        # ordering not guaranteed stable
        if 'id' in form.initial and form.initial['id'] in ivs:
            iv = ivs[form.initial['id']]
        form.extra_info = {'updated_at': iv.updated_at, 'subject_name': iv.subject_name}
    ctx = {"formset": formset, "formsethelper": forms.ImportChatFormSetHelper()}
    return render(request, 'transcripts/import.html', ctx)


@login_required
def delete(request: HttpRequest, pk: str) -> HttpResponse:
    ts = get_object_or_404(models.Transcript, pk=pk)
    if not ts.project.can_edit(request.user):
        raise PermissionDenied("User action not permitted")
    ts.deleted_at = now()
    ts.save()
    return redirect('project-responses', pk=ts.project.pk)
