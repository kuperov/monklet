from django.urls import path
from .views import (
    invitation_landing, invitation_respond
)

urlpatterns = [
    path("landing/<str:code>", invitation_landing, name="invitation-landing"),
    path("respond/<str:code>", invitation_respond, name="invitation-respond"),
]
