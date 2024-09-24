import logging

from django.shortcuts import render, redirect
from django.urls import reverse_lazy

from apps.context_helpers import blank_context, front_context
from apps.pages.forms import EnquiryForm

logger = logging.getLogger(__name__)


def make_error_handler(status):
    http_status_codes = {
        400: ("Bad Request", "There was a problem with your request."),
        401: ("Unauthorized", "You must authenticate yourself to access this resource."),
        403: ("Forbidden", "You do not have permission to access this resource."),
        404: ("Not Found", "The requested resource could not be found."),
        500: ("Internal Server Error", "An unexpected error occurred on the server."),
    }
    code = http_status_codes.get(status, ("Error", "An error occurred"))
    ctx = blank_context(dict(status=status, title=code[0], message=code[1]))
    if status == 500:
        def handler(request):
            logger.error('A server error occurred, returning status=500')
            return render(request, "error.html", ctx, status=status)
    else:
        def handler(request, exception=None):
            logger.error('An error occurred, returning status=%d: %s', status, exception, exc_info=True)
            return render(request, "error.html", ctx, status=status)
    return handler


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
