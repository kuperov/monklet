from django.urls import path
from .views import (
    project, project_settings, project_new, project_delete,
    project_leave, project_members, project_files, project_analysis,
    project_invite, interview,
    project_questions, project_questions_new, question_edit, question_delete,
    project_bots, project_bots_new, bot_edit, bot_delete,
    project_consent_letters, project_consent_letters_new, consent_letter_edit, consent_letter_delete,
    project_interviews_invited, project_interviews_invite, project_interviews_sessions
)


urlpatterns = [
    path("projects/<str:pk>/", project, name="project"),
    path("projects/<str:pk>/settings", project_settings, name="project-settings"),
    path("projects/new", project_new, name="project-new"),
    path("projects/<str:pk>/delete", project_delete, name="project-delete"),
    path("projects/<str:pk>/leave", project_leave, name="project-leave"),
    path("projects/<str:pk>/members", project_members, name="project-members"),
    path("projects/<str:pk>/analysis", project_analysis, name="project-analysis"),
    path("projects/<str:pk>/files", project_files, name="project-files"),
    path("projects/<str:pk>/invite", project_invite, name="project-invite"),
    path("interviews/<str:interview_code>", interview, name="interview"),

    path("projects/<str:pk>/questions", project_questions, name="project-questions"),
    path("projects/<str:pk>/questions/new", project_questions_new, name="project-questions-new"),
    path("question/<str:pk>/edit", question_edit, name="question-edit"),
    path("question/<str:pk>/delete", question_delete, name="question-delete"),

    path("projects/<str:pk>/bots", project_bots, name="project-bots"),
    path("projects/<str:pk>/bots/new", project_bots_new, name="project-bots-new"),
    path("bot/<str:pk>/edit", bot_edit, name="bot-edit"),
    path("bot/<str:pk>/delete", bot_delete, name="bot-delete"),

    path("projects/<str:pk>/consent-letters", project_consent_letters, name="project-consent-letters"),
    path("projects/<str:pk>/consent-letters/new", project_consent_letters_new, name="project-consent-letters-new"),
    path("consent-letters/<str:pk>/edit", consent_letter_edit, name="consent-letter-edit"),
    path("consent-letters/<str:pk>/delete", consent_letter_delete, name="consent-letter-delete"),

    path("projects/<str:pk>/invitations", project_interviews_invited, name="project-invitations"),
    path("projects/<str:pk>/invitations/invite", project_interviews_invite, name="project-interviews-invite"),
    path("projects/<str:pk>/responses", project_interviews_sessions, name="project-responses"),
]
