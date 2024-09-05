from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from web_project.template_helpers.theme import TemplateHelper
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpRequest, HttpResponse

from .models import Profile
from .forms import ProfileForm


def menu():
    return {
        'menu': [
            {'url': '/profile/', 'icon': 'menu-icon tf-icons ri-home-line', 'name': 'My projects'},
            {'url': reverse_lazy('project-new'), 'icon': 'menu-icon tf-icons ri-message-line', 'name': 'New project'},
        ]
    }

@login_required
def profile(request: HttpRequest) -> HttpResponse:
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=request.user)
        profile.save()
    ctx = {
        "profile": profile,
        "menu_data": menu(),
        "date_joined": request.user.date_joined.strftime("%d %b, %Y")
    }
    ctx['layout_path'] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "profile/profile.html", ctx)

@login_required
def profile_edit(request: HttpRequest, pk: str) -> HttpResponse:
    profile = get_object_or_404(Profile, pk=pk)
    if not request.user.is_superuser and profile.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this page.")
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    ctx = {
        'form': form,
        "menu_data": menu(),
    }
    ctx['layout_path'] = TemplateHelper.set_layout("layout_vertical.html", ctx)
    return render(request, "profile/profile-edit.html", ctx)
