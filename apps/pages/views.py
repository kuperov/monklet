import logging

from django.shortcuts import render, redirect
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


def make_error_handler(status):
    http_status_codes = {
        400: ("Bad Request", "There was a problem with your request."),
        401: (
            "Unauthorized",
            "You must authenticate yourself to access this resource.",
        ),
        403: ("Forbidden", "You do not have permission to access this resource."),
        404: ("Not Found", "The requested resource could not be found."),
        500: ("Internal Server Error", "An unexpected error occurred on the server."),
    }
    code = http_status_codes.get(status, ("Error", "An error occurred"))
    ctx = dict(status=status, title=code[0], message=code[1])
    if status == 500:

        def handler(request):
            logger.error("A server error occurred, returning status=500")
            return render(request, "error.html", ctx, status=status)

    else:

        def handler(request, exception=None):
            logger.error(
                "An error occurred, returning status=%d: %s",
                status,
                exception,
                exc_info=True,
            )
            return render(request, "error.html", ctx, status=status)

    return handler


def index(request):
    if request.user.is_authenticated:
        return redirect(reverse_lazy("users:profile"))
    return render(request, "index.html")
