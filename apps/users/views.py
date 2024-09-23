from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseForbidden, HttpRequest, HttpResponse

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import UpdateView

from apps.users.models import Profile, User
from apps.users.forms import ProfileForm
from apps.context_helpers import backend_context


def menu():
    return {
        "menu": [
            {
                "url": reverse_lazy("users:profile"),
                "icon": "menu-icon tf-icons ri-home-line",
                "name": "Home",
            },
        ]
    }


@login_required
def profile(request: HttpRequest) -> HttpResponse:
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = Profile(user=request.user)
        profile.save()
    ctx = backend_context(
        {
            "profile": profile,
            "menu_data": menu(),
            "date_joined": request.user.date_joined.strftime("%d %b, %Y"),
        }
    )
    return render(request, "profile/profile.html", ctx)


@login_required
def profile_edit(request: HttpRequest, pk: str) -> HttpResponse:
    profile = get_object_or_404(Profile, pk=pk)
    if not request.user.is_superuser and profile.user != request.user:
        return HttpResponseForbidden("You are not authorized to access this page.")
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully")
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=profile)
    ctx = backend_context(
        {
            "form": form,
            "menu_data": menu(),
        }
    )
    return render(request, "profile/profile-edit.html", ctx)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated  # type guard
        return self.request.user


user_update_view = UserUpdateView.as_view()


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.request.user.pk})


user_redirect_view = UserRedirectView.as_view()
