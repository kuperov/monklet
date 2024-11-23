from django.core.exceptions import PermissionDenied, BadRequest
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now

from apps.projects import models, forms
from apps.projects.views.util import get_editable_project


@login_required
def index(request, pk):
    case = get_object_or_404(models.Case, pk=pk)
    project = case.project
    if not project.can_view(request.user):
        raise PermissionError("Operation not permitted")
    return render(request, "case/index.html", {"project": project, "case": case})


@login_required
def delete_record(request, pk):
    record = get_object_or_404(models.Record, pk=pk)
    record.deleted_at = now()
    record.save()
    if not record.project.can_edit(request.user):
        raise PermissionError("Operation not permitted")
    messages.success(request, "Record deleted")
    return render(
        request,
        "case/_case_card.html",
        {"project": record.project, "case": record.case},
    )


@login_required
def new_note(request, pk):
    case = get_object_or_404(models.Case, pk=pk)
    project = case.project
    if not project.can_edit(request.user):
        raise PermissionError("Operation not permitted")
    if request.method == "POST":
        form = forms.CaseFollowupRecordForm(request.POST)
        if form.is_valid():
            models.Record.objects.create(
                case=case,
                project=project,
                content={"markdown": form.cleaned_data["markdown"]},
                record_type="note",
            )
            messages.success(request, "Record created")
            return render(
                request, "case/_case_card.html", {"project": project, "case": case}
            )
    else:
        form = forms.CaseFollowupRecordForm()
    return render(
        request,
        "case/_new_note.html",
        {"project": project, "case": case, "form": form},
    )


@login_required
def edit_note(request, pk):
    note = get_object_or_404(models.Record, pk=pk)
    if not isinstance(note.content, dict):
        note.content = dict()
    project = note.project
    if not project.can_edit(request.user):
        raise PermissionError("Operation not permitted")
    if request.method == "POST":
        form = forms.CaseFollowupRecordForm(request.POST)
        if form.is_valid():
            note.content["markdown"] = form.cleaned_data["markdown"]
            note.save()
            messages.success(request, "Record updated")
            return render(
                request, "case/_case_card.html", {"project": project, "case": note.case}
            )
    else:
        form = forms.CaseFollowupRecordForm(
            initial={"markdown": note.content.get("markdown")}
        )
    return render(
        request,
        "case/_edit_note.html",
        {"project": project, "note": note, "form": form},
    )


@login_required
def new_case(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_editable_project(request, pk=pk)
    if request.method == "POST":
        form = forms.ManualCaseForm(request.POST)
        if form.is_valid():
            models.Case.objects.create(
                project=project,
                real_name=form.cleaned_data["real_name"],
                pseudonym=form.cleaned_data["pseudonym"],
                description=form.cleaned_data["description"],
            )
            messages.success(request, "Case created")
            return render(request, "data/_cases.html", {"project": project})
    else:
        form = forms.ManualCaseForm()
    return render(request, "data/_new.html", {"form": form, "project": project})


@login_required
def show_line(request: HttpRequest, pk: str, line: str) -> HttpResponse:
    record = get_object_or_404(models.Record, pk=pk)
    project = record.project
    if not project.can_view(request.user):
        raise PermissionDenied("Operation not permitted")
    msgs = list(filter(lambda m: m["id"] == line, record.content))
    if not msgs:
        raise BadRequest("Invalid message id")
    msg = msgs[0]
    ctx = {"project": project, "record": record, "msg": msg}
    return render(request, "case/_ai_chat_row.html", ctx)


@login_required
def edit_line(request: HttpRequest, pk: str, line: str) -> HttpResponse:
    record = get_object_or_404(models.Record, pk=pk)
    project = record.project
    if not project.can_edit(request.user):
        raise PermissionDenied("Operation not permitted")
    msgs = list(filter(lambda m: m["id"] == line, record.content))
    if not msgs:
        raise BadRequest("Invalid message id")
    msg = msgs[0]
    if request.method == "POST":
        form = forms.ChatLineForm(request.POST)
        if form.is_valid():
            msg["text"] = form.cleaned_data["text"]
            record.save()
            ctx = {"project": project, "record": record, "msg": msg}
            return render(request, "case/_ai_chat_row.html", ctx)
    else:
        form = forms.ChatLineForm(initial={"text": msg["text"]})
    ctx = {"project": project, "form": form, "pk": pk, "msg": msg}
    return render(request, "case/_edit_chat_row.html", ctx)
