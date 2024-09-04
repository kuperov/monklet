from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/interviews/(?P<interview_code>\w+)/$", consumers.InterviewConsumer.as_asgi()),
]
