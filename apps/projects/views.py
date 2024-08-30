
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from web_project.template_helpers.theme import TemplateHelper
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.timezone import now
from django.http import HttpResponseForbidden

from .models import Project
from .forms import ProjectForm


def menu(project: Project):
    menu = [{'url': '/profile/', 'icon': 'menu-icon tf-icons ri-home-line', 'name': 'Home'}]
    if project:
        menu += [
            {'menu_header': "Current project"},
            {'url': project.url(), 'icon': 'menu-icon tf-icons ri-dashboard-line', 'name': 'Dashboard'},
            {'url': project.settings_url(), 'icon': 'menu-icon tf-icons ri-settings-2-line', 'name': 'Project settings'},
            {'url': project.members_url(), 'icon': 'menu-icon tf-icons ri-group-3-line', 'name': 'Members'},
            {'url': '#letters', 'icon': 'menu-icon tf-icons ri-heart-3-line', 'name': 'Consent letters'},
            {'menu_header': 'Design'},
            {'url': project.questions_url(), 'icon': 'menu-icon tf-icons ri-question-line', 'name': 'Questions'},
            {'url': project.bots_url(), 'icon': 'menu-icon tf-icons ri-robot-2-line', 'name': 'Bots'},
            {'url': project.invitations_url(), 'icon': 'menu-icon tf-icons ri-mail-send-line', 'name': 'Invitations'},
            {'menu_header': 'Data'},
            {'url': project.responses_url(), 'icon': 'menu-icon tf-icons ri-message-line', 'name': 'Bot sessions'},
            {'url': project.files_url(), 'icon': 'menu-icon tf-icons ri-file-upload-line', 'name': 'Uploaded transcripts'},
            {'menu_header': 'Analysis'},
            {'url': project.analysis_url(), 'icon': 'menu-icon tf-icons ri-bar-chart-box-line', 'name': 'Analysis'},
    ]
    menu += [{'menu_header': 'Session'},
            {'url': '/admin/', 'icon': 'menu-icon tf-icons ri-tools-line', 'name': 'Site administration'},
            {'url': 'account', 'icon': 'menu-icon tf-icons ri-account-box-line', 'name': 'My account'},
            {'url': reverse_lazy('account_logout'), 'icon': 'menu-icon tf-icons ri-logout-box-r-line', 'name': 'Log out'},
    ]
    return {'menu': menu}

@login_required
@permission_required('projects.view', raise_exception=True)
def project(request, pk):
    proj = get_object_or_404(Project, pk=pk, owner=request.user)
    ctx = {
        "project": proj,
        "menu_data": menu(proj)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/project.html", ctx)

@login_required
def project_settings(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
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
        "menu_data": menu(project=project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/detail.html", ctx)

@login_required
def project_new(request):
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
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    # check: does this enforce owner?
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
def project_leave(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise HttpResponseForbidden("User action not permitted.")
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
def project_members(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/members.html", ctx)

@login_required
def project_data(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/data.html", ctx)

@login_required
def project_bots(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/bots.html", ctx)

@login_required
def project_analysis(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.can_view(request.user):
        raise HttpResponseForbidden("User action not permitted.")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/analysis.html", ctx)


@login_required
def project_invitations(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/invitations.html", ctx)

@login_required
def project_questions(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/questions.html", ctx)

@login_required
def project_responses(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if not project.is_member(request.user):
        return redirect("profile")
    ctx = {
        "project": project,
        "menu_data": menu(project)
    }
    ctx["layout_path"] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "projects/responses.html", ctx)
