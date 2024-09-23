from django.urls import path
from .views import (
    lund_questions,
    project,
    project_settings,
    project_new,
    project_delete,
    project_leave,
    project_members,
    project_files,
    project_analysis,
    project_invite,
    project_resend_invitation,
    project_cancel_invitation,
    interview,
    interview_delete,
    interview_landing,
    interview_conversation,
    project_questions,
    project_questions_new,
    question_edit,
    question_delete,
    project_bots,
    project_bots_new,
    bot_edit,
    bot_delete,
    bot_public,
    project_consent_letters,
    project_consent_letters_new,
    consent_letter_edit,
    consent_letter_delete,
    consent_letter_public,
    project_interviews_invited,
    project_interviews_invite,
    project_interviews_list,
    project_simulate,
    project_transcripts,
    project_transcripts_upload,
    invitation_landing,
    invitation_respond,
    test_interviews_json,
    interview_messages,
    projects_export_interviews,
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
    path(
        "invitations/<str:pk>/resend",
        project_resend_invitation,
        name="invitation-resend",
    ),
    path(
        "invitations/<str:pk>/cancel",
        project_cancel_invitation,
        name="invitation-cancel",
    ),
    path("interviews/<str:interview_code>", interview, name="interview"),
    path("interviews/<str:pk>/delete", interview_delete, name="interview-delete"),
    path("interviews/<str:pk>/landing", interview_landing, name="interview-landing"),
    path("interviews/<str:pk>/lund", lund_questions, name="lund-questions"),
    path(
        "interviews/<str:pk>/conversation",
        interview_conversation,
        name="interview-conversation",
    ),
    path("interviews/<str:pk>/messages", interview_messages, name="interview-messages"),
    path(
        "projects/<str:pk>/export", projects_export_interviews, name="export-interviews"
    ),
    path("projects/<str:pk>/questions", project_questions, name="project-questions"),
    path(
        "projects/<str:pk>/questions/new",
        project_questions_new,
        name="project-questions-new",
    ),
    path("question/<str:pk>/edit", question_edit, name="question-edit"),
    path("question/<str:pk>/delete", question_delete, name="question-delete"),
    path("projects/<str:pk>/simulate", project_simulate, name="projects-simulate"),
    path("projects/<str:pk>/bots", project_bots, name="project-bots"),
    path("projects/<str:pk>/bots/new", project_bots_new, name="project-bots-new"),
    path("bots/<str:pk>/edit", bot_edit, name="bot-edit"),
    path("bots/<str:pk>/delete", bot_delete, name="bot-delete"),
    path("bots/<str:pk>/public", bot_public, name="bot-public"),
    path(
        "projects/<str:pk>/consent-letters",
        project_consent_letters,
        name="project-consent-letters",
    ),
    path(
        "projects/<str:pk>/consent-letters/new",
        project_consent_letters_new,
        name="project-consent-letters-new",
    ),
    path(
        "consent-letters/<str:pk>/edit", consent_letter_edit, name="consent-letter-edit"
    ),
    path(
        "consent-letter/<str:pk>", consent_letter_public, name="consent-letter-public"
    ),
    path(
        "consent-letters/<str:pk>/delete",
        consent_letter_delete,
        name="consent-letter-delete",
    ),
    path(
        "projects/<str:pk>/invitations",
        project_interviews_invited,
        name="project-invitations",
    ),
    path(
        "projects/<str:pk>/invitations/invite",
        project_interviews_invite,
        name="project-interviews-invite",
    ),
    path(
        "projects/<str:pk>/interviews",
        project_interviews_list,
        name="project-interviews-list",
    ),
    path(
        "projects/<str:pk>/test_interviews",
        test_interviews_json,
        name="project-interviews-test-json",
    ),
    path(
        "projects/<str:pk>/transcripts", project_transcripts, name="project-responses"
    ),
    path(
        "projects/<str:pk>/transcripts/upload",
        project_transcripts_upload,
        name="project-transcripts-upload",
    ),
    path(
        "collaborate/landing/<str:code>", invitation_landing, name="invitation-landing"
    ),
    path(
        "collaborate/respond/<str:code>", invitation_respond, name="invitation-respond"
    ),
]
