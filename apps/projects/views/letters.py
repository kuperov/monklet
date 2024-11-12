from django.contrib import messages
from apps.context_helpers import backend_context, blank_context
from apps.projects.forms import ConsentLetterForm
from apps.projects.models import ConsentLetter, Project


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


@login_required
def project_consent_letters(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({"project": project})
    return render(request, "consent_letters/list.html", ctx)


@login_required
def project_consent_letters_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ConsentLetterForm(request.POST)
        if form.is_valid:
            let = form.save(commit=False)
            let.project = project
            let.save()
            messages.add_message(request, messages.SUCCESS, "Consent letter added")
            return redirect("project-consent-letters", pk=project.pk)
    else:
        form = ConsentLetterForm()
    ctx = backend_context(
        {"form": form, "project": project}
    )
    return render(request, "consent_letters/detail.html", ctx)


@login_required
def consent_letter_edit(request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    if request.method == "POST":
        form = ConsentLetterForm(request.POST, instance=consent_letter)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated consent_letter")
            return redirect("project-consent-letters", pk=consent_letter.project.pk)
    else:
        form = ConsentLetterForm(instance=consent_letter)
    ctx = backend_context({"form": form, "project": consent_letter.project})
    return render(request, "consent_letters/detail.html", ctx)


def consent_letter_public(request: HttpRequest, pk: str) -> HttpRequest:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    ctx = blank_context({"project": consent_letter.project, "letter": consent_letter})
    return render(request, "consent_letters/public.html", ctx)


@login_required
def consent_letter_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    project_id = consent_letter.project.pk
    consent_letter.delete()
    return redirect("project-consent-letters", pk=project_id)
