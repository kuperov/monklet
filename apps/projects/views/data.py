from django.contrib import messages
from apps.projects import forms, models

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.timezone import now

from apps.projects.views.util import get_editable_project, get_viewable_project


@login_required
def index(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk=pk)
    return render(request, "data/index.html", {"project": project})


@login_required
def cases(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_viewable_project(request, pk=pk)

    return render(request, "data/_cases.html", {"project": project})


@login_required
def new_empty(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk=pk)
    if request.method == "POST":
        form = forms.ManualTranscriptForm(request.POST)
        if form.is_valid():
            models.Case.objects.create(
                project=project,
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
            )
            messages.success(request, "Case created")
            return render(request, "data/_cases.html", {"project": project})
    else:
        form = forms.ManualTranscriptForm()
    return render(request, "data/_new.html", {"form": form, "project": project})


@login_required
def import_chats(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk)
    already_imported = set(
        [t.interview_id for t in project.records.filter(deleted_at=None)]
    )
    ivs = {
        iv.pk: iv
        for iv in project.started_completed_interviews()
        if iv.pk not in already_imported
    }
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
                        _ts = models.Case.from_chat(
                            chat, pseudonym=iv.cleaned_data["pseudonym"]
                        )
                messages.success(
                    request,
                    f"Created {num_imported} case(s), each with one transcript record",
                )
                return render(request, "data/_cases.html", {"project": project})
    else:
        # list unimported interviews, come up with pseudonyms
        initial = [
            {"id": k, "pseudonym": iv.subject_name, "selected": False}
            for k, iv in ivs.items()
        ]
        formset = forms.ImportChatFormSet(initial=initial)

    # read-only fields not passed through in GET data
    for form, iv in zip(formset, ivs.values()):
        # ordering not guaranteed stable
        if "id" in form.initial and form.initial["id"] in ivs:
            iv = ivs[form.initial["id"]]
        form.extra_info = {"updated_at": iv.updated_at, "subject_name": iv.subject_name}
    ctx = {
        "formset": formset,
        "formsethelper": forms.ImportChatFormSetHelper(),
        "project": project,
        "available": len(formset) > 0,
    }
    return render(request, "data/_import.html", ctx)


@login_required
def delete_case(request: HttpRequest, pk: str) -> HttpResponse:
    ts = get_object_or_404(models.Case, pk=pk)
    if not ts.project.can_edit(request.user):
        raise PermissionDenied("User action not permitted")
    ts.deleted_at = now()
    ts.save()
    messages.success("Case deleted")
    return render(request, "data/_cases.html", {"project": ts.project})
