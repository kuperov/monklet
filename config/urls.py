from django.contrib import admin
from django.urls import include, path
from apps.pages.views import make_error_handler
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
    path("users/", include("apps.users.urls")),
    path("", include("apps.projects.urls")),
    path("accounts/", include("allauth.urls")),
]

handler404 = make_error_handler(status=404)
handler401 = make_error_handler(status=401)
handler403 = make_error_handler(status=403)
handler400 = make_error_handler(status=400)
handler500 = make_error_handler(status=500)

if settings.DEBUG or settings.TEST_RUNNER:
    urlpatterns += [
        path("404", handler404),
        path("401", handler401),
        path("403", handler403),
        path("400", handler400),
        path("500", handler500),
    ]
