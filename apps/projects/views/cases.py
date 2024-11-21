from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
def new_followup(request, pk):
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
            )
            messages.success("Record created")
            return redirect("case", pk=case.pk)
    else:
        form = forms.CaseFollowupRecordForm()
    return render(
        request,
        "case/_new_record.html",
        {"project": project, "case": case, "form": form},
    )


@login_required
def edit_followup(request, pk):
    record = get_object_or_404(models.Record, pk=pk)
    project = record.project
    if not project.can_edit(request.user):
        raise PermissionError("Operation not permitted")
    if request.method == "POST":
        form = forms.CaseFollowupRecordForm(request.POST)
        if form.is_valid():
            record.content["markdown"] = form.cleaned_data["markdown"]
            record.save()
            messages.success(request, "Record updated")
            return redirect("case", pk=record.case.pk)
    else:
        form = forms.CaseFollowupRecordForm()
    return render(
        request,
        "case/_edit_record.html",
        {"project": project, "record": record, "form": form},
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
