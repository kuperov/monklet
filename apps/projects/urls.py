from django.urls import path

from apps.projects.views import interviews, analysis, projects, members, questions, bots, transcripts, letters


urlpatterns = [
    path("projects/<str:pk>/", projects.project, name="project"),
    path("projects/<str:pk>/settings", projects.project_settings, name="project-settings"),
    path("projects/new", projects.project_new, name="project-new"),
    path("projects/<str:pk>/delete", projects.project_delete, name="project-delete"),
    path("projects/<str:pk>/leave", projects.project_leave, name="project-leave"),

    path("projects/<str:pk>/members", members.project_members, name="project-members"),
    path("projects/<str:pk>/invite", members.project_invite, name="project-invite"),
    path(
        "invitations/<str:pk>/resend",
        members.project_resend_invitation,
        name="invitation-resend",
    ),
    path(
        "invitations/<str:pk>/cancel",
        members.project_cancel_invitation,
        name="invitation-cancel",
    ),
    path(
        "collaborate/landing/<str:code>", members.invitation_landing, name="invitation-landing"
    ),
    path(
        "collaborate/respond/<str:code>", members.invitation_respond, name="invitation-respond"
    ),

    path("projects/<str:pk>/questions", questions.project_questions, name="project-questions"),
    path(
        "projects/<str:pk>/questions/new",
        questions.project_questions_new,
        name="project-questions-new",
    ),
    path("question/<str:pk>/edit", questions.question_edit, name="question-edit"),
    path("question/<str:pk>/delete", questions.question_delete, name="question-delete"),

    path("projects/<str:pk>/simulate", bots.project_simulate, name="projects-simulate"),
    path("projects/<str:pk>/bots", bots.project_bots, name="project-bots"),
    path("projects/<str:pk>/bots/new", bots.project_bots_new, name="project-bots-new"),
    path("bots/<str:pk>/edit", bots.bot_edit, name="bot-edit"),
    path("bots/<str:pk>/delete", bots.bot_delete, name="bot-delete"),
    path("bots/<str:pk>/duplicate", bots.bot_duplicate, name="bot-duplicate"),
    path("bots/<str:pk>/public", bots.bot_public, name="bot-public"),

    path(
        "projects/<str:pk>/consent-letters",
        letters.project_consent_letters,
        name="project-consent-letters",
    ),
    path(
        "projects/<str:pk>/consent-letters/new",
        letters.project_consent_letters_new,
        name="project-consent-letters-new",
    ),
    path(
        "consent-letters/<str:pk>/edit", letters.consent_letter_edit, name="consent-letter-edit"
    ),
    path(
        "consent-letter/<str:pk>", letters.consent_letter_public, name="consent-letter-public"
    ),
    path(
        "consent-letters/<str:pk>/delete",
        letters.consent_letter_delete,
        name="consent-letter-delete",
    ),

    path("interviews/<str:interview_code>", interviews.interview, name="interview"),
    path("interviews/<str:pk>/delete", interviews.interview_delete, name="interview-delete"),
    path("interviews/<str:pk>/landing", interviews.interview_landing, name="interview-landing"),
    path("interviews/<str:pk>/lund", interviews.lund_questions, name="lund-questions"),
    path(
        "interviews/<str:pk>/conversation",
        interviews.interview_conversation,
        name="interview-conversation",
    ),
    path("interviews/<str:pk>/messages", interviews.interview_messages, name="interview-messages"),
    path(
        "projects/<str:pk>/export", interviews.projects_export_interviews, name="export-interviews"
    ),
    path(
        "projects/<str:pk>/invitations",
        interviews.project_interviews_invited,
        name="project-invitations",
    ),
    path(
        "projects/<str:pk>/invitations/invite",
        interviews.project_interviews_invite,
        name="project-interviews-invite",
    ),
    path(
        "projects/<str:pk>/interviews",
        interviews.project_interviews_list,
        name="project-interviews-list",
    ),
    path(
        "projects/<str:pk>/test_interviews",
        interviews.test_interviews_json,
        name="project-interviews-test-json",
    ),

    path(
        "projects/<str:pk>/transcripts", transcripts.project_transcripts, name="project-responses"
    ),
    path(
        "projects/<str:pk>/transcripts/upload",
        transcripts.project_transcripts_upload,
        name="project-transcripts-upload",
    ),

    path("projects/<str:pk>/analysis", analysis.project_analysis, name="project-analysis"),
]
