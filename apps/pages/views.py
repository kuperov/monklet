from django.views.generic import TemplateView

from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from web_project import TemplateLayout
from web_project.template_helpers.theme import TemplateHelper

from .forms import EnquiryForm
from apps.context_helpers import front_context


class PagesView(TemplateView):
    def get_context_data(self, **kwargs):
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context.update(
            {
                "layout_path": TemplateHelper.set_layout("layout_blank.html", context),
            }
        )
        return context


def landing_page(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("users:profile"))
    else:
        form = EnquiryForm()
        ctx = front_context({'form': form})
        return render(request, "landing_page.html", ctx)


def enquiry_partial(request):
    if request.method == "POST":
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            # TODO: send email
            return render(request, "_enquiry.html", {'success': True})
    else:
        form = EnquiryForm()
    return render(request, "_enquiry.html", {'form': form, 'success': False})
