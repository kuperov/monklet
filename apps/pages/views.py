
from django.views.generic import TemplateView
from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy

from .forms import EnquiryForm
from apps.context_helpers import blank_context

class PagesView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )
        return context


class LandingPageView(PagesView):
    template_name = "landing_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            return redirect(reverse_lazy('users:profile'))
        return context


def comingsoon(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy('users:profile'))
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse_lazy("enquiry_success"))
    else:
        form = EnquiryForm()

    ctx = blank_context()
    ctx.update({"form": form})
    return render(request, "comingsoon.html", ctx)


def enquiry_success(request):
    ctx = blank_context()
    return render(request, "enquiry_success.html", ctx)
