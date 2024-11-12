from django.urls import path

from apps.projects.views import interviews, analysis, projects, members, questions, bots, transcripts, letters


urlpatterns = [
    path("projects/<str:pk>/", projects.dashboard, name="project"),
    path("projects/<str:pk>/settings", projects.settings, name="project-settings"),
    path("projects/new", projects.new, name="project-new"),
    path("projects/<str:pk>/delete", projects.delete, name="project-delete"),
    path("projects/<str:pk>/leave", projects.leave, name="project-leave"),

    path("projects/<str:pk>/members", members.list, name="project-members"),
    path("projects/<str:pk>/invite", members.invite, name="project-invite"),
    path(
        "invitations/<str:pk>/resend",
        members.resend_invitation,
        name="invitation-resend",
    ),
    path(
        "invitations/<str:pk>/cancel",
        members.cancel_invitation,
        name="invitation-cancel",
    ),
    path(
        "collaborate/landing/<str:code>", members.invitation_landing, name="invitation-landing"
    ),
    path(
        "collaborate/respond/<str:code>", members.invitation_respond, name="invitation-respond"
    ),

    path("projects/<str:pk>/questions", questions.list, name="project-questions"),
    path(
        "projects/<str:pk>/questions/new",
        questions.new,
        name="project-questions-new",
    ),
    path("question/<str:pk>/edit", questions.edit, name="question-edit"),
    path("question/<str:pk>/delete", questions.delete, name="question-delete"),

    path("projects/<str:pk>/simulate", bots.simulate, name="projects-simulate"),
    path("projects/<str:pk>/bots", bots.list, name="project-bots"),
    path("projects/<str:pk>/bots/new", bots.new, name="project-bots-new"),
    path("bots/<str:pk>/edit", bots.edit, name="bot-edit"),
    path("bots/<str:pk>/delete", bots.delete, name="bot-delete"),
    path("bots/<str:pk>/duplicate", bots.duplicate, name="bot-duplicate"),
    path("bots/<str:pk>/public", bots.landing_public, name="bot-public"),

    path(
        "projects/<str:pk>/consent-letters",
        letters.list,
        name="project-consent-letters",
    ),
    path(
        "projects/<str:pk>/consent-letters/new",
        letters.new,
        name="project-consent-letters-new",
    ),
    path(
        "consent-letters/<str:pk>/edit", letters.edit, name="consent-letter-edit"
    ),
    path(
        "consent-letter/<str:pk>", letters.public, name="consent-letter-public"
    ),
    path(
        "consent-letters/<str:pk>/delete",
        letters.delete,
        name="consent-letter-delete",
    ),

    path("interviews/<str:interview_code>", interviews.landing_invited, name="interview"),
    path("interviews/<str:pk>/delete", interviews.delete, name="interview-delete"),
    path("interviews/<str:pk>/landing", interviews.uninvited_landing, name="interview-landing"),
    path("interviews/<str:pk>/lund", interviews.lund_questions, name="lund-questions"),
    path(
        "interviews/<str:pk>/conversation",
        interviews.conversation,
        name="interview-conversation",
    ),
    path("interviews/<str:pk>/messages", interviews.messages_json, name="interview-messages"),
    path(
        "projects/<str:pk>/export", interviews.export, name="export-interviews"
    ),
    path(
        "projects/<str:pk>/invitations",
        interviews.list_invited,
        name="project-invitations",
    ),
    path(
        "projects/<str:pk>/invitations/invite",
        interviews.invite,
        name="project-interviews-invite",
    ),
    path(
        "projects/<str:pk>/interviews",
        interviews.list,
        name="project-interviews-list",
    ),
    path(
        "projects/<str:pk>/test_interviews",
        interviews.list_json,
        name="project-interviews-test-json",
    ),

    path(
        "projects/<str:pk>/transcripts", transcripts.list, name="project-responses"
    ),
    path(
        "projects/<str:pk>/transcripts/upload",
        transcripts.new,
        name="project-transcripts-upload",
    ),

    path("projects/<str:pk>/analysis", analysis.project_analysis, name="project-analysis"),
]
