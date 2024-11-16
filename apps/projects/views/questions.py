from django.contrib import messages
from apps.projects.forms import QuestionForm
from apps.projects.models import Project, Question


from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render


@login_required
def list(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    return render(request, "questions/list.html", {"project": project})


@login_required
def new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid:
            q = form.save(commit=False)
            q.project = project
            q.order = 1 + project.questions.count()
            q.save()
            messages.add_message(request, messages.SUCCESS, "Question added")
            return redirect("project-questions", pk=project.pk)
    else:
        form = QuestionForm()
    ctx = {"form": form, "project": project}
    return render(request, "questions/detail.html", ctx)


@login_required
def edit(request: HttpRequest, pk: str) -> HttpResponse:
    question = get_object_or_404(Question, pk=pk)
    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated question")
            return redirect("project-questions", pk=question.project.pk)
    else:
        form = QuestionForm(instance=question)
    ctx = {"form": form, "project": question.project}
    return render(request, "questions/detail.html", ctx)


@login_required
def delete(_request: HttpRequest, pk: str) -> HttpResponse:
    question = get_object_or_404(Question, pk=pk)
    project_id = question.project.pk
    question.delete()
    return redirect("project-questions", pk=project_id)
