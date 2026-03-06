from django.urls import path
from apps.pages.views import index


urlpatterns = [
    path("", index, name="index"),
]
