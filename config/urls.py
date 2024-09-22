from django.contrib import admin
from django.urls import include, path
from web_project.views import SystemView
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("users/", include("apps.users.urls")),
    path("", include("apps.projects.urls")),
    path("accounts/", include("allauth.urls")),
]

handler404 = SystemView.as_view(template_name="pages_misc_error.html", status=404)
handler403 = SystemView.as_view(template_name="pages_misc_not_authorized.html", status=403)
handler400 = SystemView.as_view(template_name="pages_misc_error.html", status=400)
handler500 = SystemView.as_view(template_name="pages_misc_error.html", status=500)

if settings.DEBUG:
    urlpatterns += [
        path("404", handler404),
        path("403", handler403),
        path("400", handler400),
        path("500", handler500),
    ]
