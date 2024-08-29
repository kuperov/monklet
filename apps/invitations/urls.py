from django.urls import path
from .views import (
    invitation_landing
)

urlpatterns = [
    path("landing/<str:code>", invitation_landing, name="invitation-landing"),
]
