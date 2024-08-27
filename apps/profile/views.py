from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from web_project.template_helpers.theme import TemplateHelper
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.contrib import messages

from apps.projects.models import Project
from .models import Profile
from .forms import ProfileForm


def menu():
    return {
        'menu': [
            {'url': '/profile/', 'icon': 'menu-icon tf-icons ri-home-line', 'name': 'Home'},
            {'url': reverse_lazy('project-new'), 'icon': 'menu-icon tf-icons ri-message-line', 'name': 'New project'},
            {'menu_header': 'Session'},
            {'url': '/admin/', 'icon': 'menu-icon tf-icons ri-tools-line', 'name': 'Admin'},
            {'url': 'asf', 'icon': 'menu-icon tf-icons ri-account-box-line', 'name': 'My account'},
            {'url': reverse_lazy('account_logout'), 'icon': 'menu-icon tf-icons ri-logout-box-r-line', 'name': 'Log out'},
        ]
    }

@login_required
def profile(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=request.user)
        profile.save()
    projects = Project.objects.filter(owner=request.user, deleted_at=None)
    ctx = {
        "projects": projects,
        "menu_data": menu(),
        "date_joined": request.user.date_joined.strftime("%d %b, %Y")
    }
    #ctx['layout_path'] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "profile/profile.html", ctx)

@login_required
def profile_edit(request, pk):
    profile = get_object_or_404(Profile, pk=pk, user=request.user)
    if profile.user.id != request.user.id and not profile.user.is_superuser:
        return redirect('profile')
    if request.method == 'POST':
        form = ProfileForm(request.post)
        if form.is_valid:
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    ctx = {
        'form': form,
        "menu_data": menu(),
        'layout_path': TemplateHelper.set_layout("layout_vertical.html", {})
    }
    return render(request, "profile/profile-edit.html", ctx)
