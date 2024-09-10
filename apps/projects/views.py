
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from .models import Project, Interview, Question, Bot, ConsentLetter, MemberInvitation
from .forms import (
    ProjectForm, MemberInvitationForm, QuestionForm, BotForm, ConsentLetterForm,
    InterviewForm, ManualTranscriptForm, InvitationResponseForm)
from apps.context_helpers import backend_context

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
    ctx = backend_context({
        "project": proj,
        "menu_data": menu(proj)
    })
    return render(request, "projects/project.html", ctx)

@login_required
def project_settings(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.owner == request.user:
        raise PermissionDenied("User action not permitted.")
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            messages.success(request, "Project updated successfully")
            return redirect(project.url)
    else:
        form = ProjectForm(instance=project)
    ctx = backend_context({
        "form": form,
        "project": project,
        "menu_data": menu(project=project)
    })
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
    ctx = backend_context({
        "form": form,
        "menu_data": menu(project=None)
    })
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
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
    return render(request, "projects/leave.html", ctx)


@login_required
def project_members(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
    return render(request, "members/list.html", ctx)

@login_required
def project_analysis(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
    return render(request, "analysis/summary.html", ctx)


@login_required
def project_questions(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "menu_data": menu(question.project)
    })
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
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "project": project,
        "menu_data": menu(project)
    })
    return render(request, "members/invite.html", ctx)

@login_required
def project_bots(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "menu_data": menu(bot.project)
    })
    return render(request, 'bots/detail.html', ctx)

@login_required
def bot_delete(_request: HttpRequest, pk: str) -> HttpResponse:
    bot = get_object_or_404(Bot, pk=pk)
    project_id = bot.project.pk
    bot.delete()
    return redirect('project-bots', pk=project_id)

@login_required
def project_simulate(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_edit(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
    return render(request, 'bots/simulate.html', ctx)


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
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "menu_data": menu(consent_letter.project)
    })
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
    ctx = backend_context({
        "project": project,
        "interviews": interviews,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "project": project,
        "menu_data": menu(project)
    })
    return render(request, "interviews/new.html", ctx)

@login_required
def project_transcripts(request: HttpRequest, pk: str) -> HttpResponse:
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise PermissionDenied("User action not permitted.")
    ctx = backend_context({
        "project": project,
        "menu_data": menu(project)
    })
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
    ctx = backend_context({
        "form": form,
        "menu_data": menu(project)
    })
    return render(request, "transcripts/upload.html", ctx)

# at this point users are possibly unauthenticated
def invitation_landing(request: HttpRequest, code: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=code)
    if not inv.is_valid:
        return render(request, 'invitations/not_available.html')
    if request.user == inv.project.owner:  # owner clicked own link
        raise PermissionDenied("User action not permitted.")
    if not request.user.is_authenticated:
        return render(request, 'invitations/landing_not_logged_in.html', {
            'project': inv.project, 'return_url': inv.landing_url})
    else:
        # logged in, so just ask if accept
        form = InvitationResponseForm()
        form.helper.form_action = reverse_lazy('invitation-respond', kwargs={'code': code})
        ctx = {'form': form}
        return render(request, 'invitations/landing_logged_in.html', ctx)

def invitation_respond(request: HttpRequest, code: str) -> HttpResponse:
    inv = get_object_or_404(MemberInvitation, pk=code)
    if not inv.is_valid:
        return render(request, 'invitations/not_available.html')
    if request.user == inv.project.owner:  # owner clicked own link
        raise PermissionDenied("User action not permitted.")
    if not request.user.is_authenticated:
        return redirect(inv.landing_url)
    if request.method == 'POST' and request.POST.get('yes'):
        inv.accept(request.user)
        inv.save()
        return redirect(inv.project.url)
    else:
        raise PermissionDenied("User action not permitted.")
