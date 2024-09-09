
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from web_project.template_helpers.theme import TemplateHelper
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from .models import Project, Interview, Question, Bot, ConsentLetter
from .forms import (
    ProjectForm, MemberInvitationForm, QuestionForm, BotForm, ConsentLetterForm,
    InterviewForm, ManualTranscriptForm)


def menu(project: Project):
    menu = [{'url': '/profile/', 'icon': 'menu-icon tf-icons ri-home-line', 'name': 'Home'}]
    if project:
        menu += [
            {'menu_header': "Current project"},
            {'url': project.url, 'icon': 'menu-icon tf-icons ri-dashboard-line', 'name': 'Dashboard'},
            {'url': project.settings_url, 'icon': 'menu-icon tf-icons ri-settings-2-line', 'name': 'Project settings'},
            {'url': project.members_url, 'icon': 'menu-icon tf-icons ri-group-3-line', 'name': 'Members'},
            {'url': project.consent_letters_url, 'icon': 'menu-icon tf-icons ri-heart-3-line', 'name': 'Consent letters'},
            {'menu_header': 'Interview design'},
            {'url': project.questions_url, 'icon': 'menu-icon tf-icons ri-question-line', 'name': 'Questions'},
            {'url': project.bots_url, 'icon': 'menu-icon tf-icons ri-robot-2-line', 'name': 'Interview bots'},
            {'url': project.invitations_url, 'icon': 'menu-icon tf-icons ri-mail-send-line', 'name': 'Interview invitations'},
            {'menu_header': 'Analysis'},
            {'url': project.data_url, 'icon': 'menu-icon tf-icons ri-message-line', 'name': 'Data'},
            {'url': project.analysis_url, 'icon': 'menu-icon tf-icons ri-bar-chart-box-line', 'name': 'Harmonized analysis'},
    ]
    return {'menu': menu}

@login_required
#@permission_required('projects.view', raise_exception=True)
def project(request: HttpRequest, pk: str) -> HttpResponse:
    proj = get_object_or_404(Project, pk=pk)
    if not proj.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": proj,
        "menu_data": menu(proj)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/project.html", ctx)

@login_required
def project_settings(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.owner == request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully")
            return redirect(project.url())
    else:
        form = ProjectForm(instance=project)
    ctx = {
        "form": form,
        "project": project,
        "menu_data": menu(project=project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/detail.html", ctx)

@login_required
def project_new(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.instance.owner = request.user
            proj = form.save()
            return redirect(reverse_lazy("project-members", kwargs={'pk': proj.id}))
    else:
        form = ProjectForm()
        form.helper.form_acount = reverse_lazy('project-new')
    ctx = {
        "form": form,
        "menu_data": menu(project=None)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/detail.html", ctx)

@login_required
def project_delete(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if project.owner != request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        project.deleted_at = now
        project.save()
        messages.success(request, "Project {project.name} deleted.")
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/delete.html", ctx)

@login_required
def project_leave(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user) or project.owner == request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        project.members.remove(request.user)
        project.save()
        messages.success(request, f"You have been removed from {project.name}.")
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/leave.html", ctx)


@login_required
def project_members(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "members/list.html", ctx)

@login_required
def project_analysis(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "analysis/summary.html", ctx)


@login_required
def project_questions(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "questions/list.html", ctx)

@login_required
def project_questions_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid:
            q = form.save(commit=False)
            q.project = project
            q.order = 1 + project.questions.count()
            q.save()
            messages.add_message(request, messages.SUCCESS, "Question added")
            return redirect('project-questions', pk=project.pk)
    else:
        form = QuestionForm()
    ctx = {
        "form": form,
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "questions/detail.html", ctx)

@login_required
def question_edit(request: HttpRequest, pk: str) -> HttpResponse:
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated question")
            return redirect('project-questions', pk=question.project.pk)
    else:
        form = QuestionForm(instance=question)
    ctx = {
        "form": form,
        "menu_data": menu(question.project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, 'questions/detail.html', ctx)

@login_required
def question_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    question = get_object_or_404(Question, pk=pk)
    project_id = question.project.pk
    question.delete()
    return redirect('project-questions', pk=project_id)

@login_required
def project_files(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/files.html", ctx)

@login_required
def project_invite(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = MemberInvitationForm(request.POST)
        if form.is_valid():
            inv = form.save(commit=False)
            inv.project = project
            inv.send_email(request)  # saves
            messages.success(request, "Invitation sent")
            return redirect(project.members_url)
    else:
        form = MemberInvitationForm()
    ctx = {
        "form": form,
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "members/invite.html", ctx)

@login_required
def project_bots(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "bots/list.html", ctx)

@login_required
def project_bots_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == 'POST':
        form = BotForm(request.POST)
        if form.is_valid:
            b = form.save(commit=False)
            b.project = project
            b.save()
            messages.add_message(request, messages.SUCCESS, "Bot added")
            return redirect('project-bots', pk=project.pk)
    else:
        form = BotForm()
    ctx = {
        "form": form,
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "bots/detail.html", ctx)

@login_required
def bot_edit(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    if request.method == 'POST':
        form = BotForm(request.POST, instance=bot)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated bot")
            return redirect('project-bots', pk=bot.project.pk)
    else:
        form = BotForm(instance=bot)
    ctx = {
        "form": form,
        "menu_data": menu(bot.project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, 'bots/detail.html', ctx)

@login_required
def bot_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    project_id = bot.project.pk
    bot.delete()
    return redirect('project-bots', pk=project_id)

@login_required
def project_simulate(request: HttpRequest, code: str) -> HttpResponse:
    interview = get_object_or_404(Interview, pk=code)
    bot = interview.bot
    project = interview.project
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "bot": bot,
        "project": project,
        "initial_messages": [m.display() for m in interview.messages.all()],
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, 'bots/simulate.html', ctx)

@login_required
def bot_simulate_new(request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    project = bot.project
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    iv = Interview.objects.create(project=project, bot=bot, status='test')
    # TODO: construct URL with GET parameters for the new chat
    return redirect('interviews-simulate', code=iv.pk)

# note: unauthenticated view - interview_code provides security
def interview(request, interview_code):
    iv = get_object_or_404(Interview, code=interview_code)
    return render(request, "interviews/interview.html", {
        'interview_code': interview_code,
        'interview': iv,
        'messages': [m.display() for m in iv.messages]
    })


@login_required
def project_consent_letters(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "consent_letters/list.html", ctx)

@login_required
def project_consent_letters_new(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == 'POST':
        form = ConsentLetterForm(request.POST)
        if form.is_valid:
            let = form.save(commit=False)
            let.project = project
            let.save()
            messages.add_message(request, messages.SUCCESS, "Consent letter added")
            return redirect('project-consent-letters', pk=project.pk)
    else:
        form = ConsentLetterForm()
    ctx = {
        "form": form,
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "consent_letters/detail.html", ctx)

@login_required
def consent_letter_edit(request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    if request.method == 'POST':
        form = ConsentLetterForm(request.POST, instance=consent_letter)
        print(form.fields)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated consent_letter")
            return redirect('project-consent-letters', pk=consent_letter.project.pk)
    else:
        form = ConsentLetterForm(instance=consent_letter)
    ctx = {
        "form": form,
        "menu_data": menu(consent_letter.project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, 'consent_letters/detail.html', ctx)

@login_required
def consent_letter_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    consent_letter = get_object_or_404(ConsentLetter, pk=pk)
    project_id = consent_letter.project.pk
    consent_letter.delete()
    return redirect('project-consent-letters', pk=project_id)

@login_required
def project_interviews_invited(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    interviews = project.interviews.exclude(status='test')
    ctx = {
        "project": project,
        "interviews": interviews,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "interviews/invited.html", ctx)

@login_required
def project_interviews_invite(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid:
            b = form.save(commit=False)
            b.project = project
            b.save()
            messages.add_message(request, messages.SUCCESS, "Interview added")
            return redirect('project-invitations', pk=project.pk)
    else:
        form = InterviewForm()
    ctx = {
        "form": form,
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "interviews/new.html", ctx)

@login_required
def project_transcripts(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "transcripts/list.html", ctx)

@login_required
def project_transcripts_upload(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    if request.method == 'POST':
        form = ManualTranscriptForm(request.POST)
        if form.is_valid:
            ts = form.save(commit=False)
            ts.project = project
            ts.save()
            messages.add_message(request, messages.SUCCESS, "Transcript added")
            return redirect('project-transcripts', pk=project.pk)
    else:
        form = ManualTranscriptForm()
    ctx = {
        "form": form,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "transcripts/upload.html", ctx)
