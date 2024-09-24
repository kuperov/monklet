from django.urls import path
from apps.pages.views import landing_page, enquiry_partial


urlpatterns = [
    path("", landing_page, name="index"),
    path("enquiry", enquiry_partial, name="enquiry_partial"),
]
