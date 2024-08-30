from django.urls import path
from .views import (
    project, project_settings, project_new, project_delete,
    project_leave, project_members, project_files, project_analysis,
    project_bots, project_invitations, project_questions,
    project_responses
)


urlpatterns = [
    path("<str:pk>/", project, name="project"),
    path("<str:pk>/settings", project_settings, name="project-settings"),
    path("new", project_new, name="project-new"),
    path("<str:pk>/delete", project_delete, name="project-delete"),
    path("<str:pk>/leave", project_leave, name="project-leave"),
    path("<str:pk>/members", project_members, name="project-members"),
    path("<str:pk>/bots", project_bots, name="project-bots"),
    path("<str:pk>/invitations", project_invitations, name="project-invitations"),
    path("<str:pk>/analysis", project_analysis, name="project-analysis"),
    path("<str:pk>/questions", project_questions, name="project-questions"),
    path("<str:pk>/responses", project_responses, name="project-responses"),
    path("<str:pk>/files", project_files, name="project-files"),
]
