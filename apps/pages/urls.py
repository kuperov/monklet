from django.urls import path
from apps.pages.views import index, enquiry_partial


urlpatterns = [
    path("", index, name="index"),
    path("enquiry", enquiry_partial, name="enquiry_partial"),
]
