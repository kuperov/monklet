from django.urls import path

from apps.projects.views import (
    data,
    interviews,
    analysis,
    projects,
    questions,
    bots,
    settings,
    cases,
    api,
)


urlpatterns = [
    path("projects/<str:pk>/", projects.dashboard, name="project"),
    path("projects/new", projects.new, name="project-new"),
    path("projects/<str:pk>/delete", projects.delete, name="project-delete"),
    path("projects/<str:pk>/leave", projects.leave, name="project-leave"),
    path("projects/<str:pk>/settings", settings.view, name="project-settings"),
    path(
        "projects/<str:pk>/settings-tab",
        settings.settings_tab,
        name="project-settings-tab",
    ),
    path("projects/<str:pk>/invite", settings.invite, name="project-invite"),
    path("projects/<str:pk>/members", settings.members, name="project-members"),
    path(
        "projects/<str:pk>/invitations",
        settings.invitations,
        name="project-invitations",
    ),
    path(
        "invitations/<str:pk>/resend",
        settings.resend_invitation,
        name="invitation-resend",
    ),
    path(
        "invitations/<str:pk>/cancel",
        settings.cancel_invitation,
        name="invitation-cancel",
    ),
    path(
        "collaborate/landing/<str:code>",
        settings.invitation_landing,
        name="invitation-landing",
    ),
    path(
        "collaborate/respond/<str:code>",
        settings.invitation_respond,
        name="invitation-respond",
    ),
    path("projects/<str:pk>/questions", questions.list, name="project-questions"),
    path(
        "projects/<str:pk>/questions/new", questions.new, name="project-questions-new"
    ),
    path("question/<str:pk>/edit", questions.edit, name="question-edit"),
    path("question/<str:pk>/delete", questions.delete, name="question-delete"),
    # path("projects/<str:pk>/simulate", bots.simulate, name="projects-simulate"),
    path("projects/<str:pk>/bots", bots.index, name="project-bots"),
    path("projects/<str:pk>/bots/new", bots.new_bot, name="project-bots-new"),
    path("bots/<str:pk>/edit", bots.edit_bot, name="bot-edit"),
    path("bots/<str:pk>/delete", bots.delete_bot, name="bot-delete"),
    path("bots/<str:pk>/duplicate", bots.duplicate_bot, name="bot-duplicate"),
    path(
        "projects/<str:pk>/consent-letters/new",
        bots.new_letter,
        name="project-consent-letters-new",
    ),
    path("consent-letters/<str:pk>/edit", bots.edit_letter, name="consent-letter-edit"),
    path("consent-letter/<str:pk>", bots.view_letter, name="consent-letter-public"),
    path(
        "consent-letters/<str:pk>/delete",
        bots.delete_letter,
        name="consent-letter-delete",
    ),
    path("bots/<str:pk>/public", interviews.landing_public, name="bot-public"),
    path(
        "interviews/<str:interview_code>", interviews.landing_invited, name="interview"
    ),
    path("interviews/<str:pk>/delete", interviews.delete, name="interview-delete"),
    path(
        "interviews/<str:pk>/landing",
        interviews.uninvited_landing,
        name="interview-landing",
    ),
    path("interviews/<str:pk>/lund", interviews.lund_questions, name="lund-questions"),
    path(
        "interviews/<str:pk>/conversation",
        interviews.conversation,
        name="interview-conversation",
    ),
    path(
        "interviews/<str:pk>/messages",
        interviews.messages_json,
        name="interview-messages",
    ),
    path("projects/<str:pk>/export", interviews.export, name="export-interviews"),
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
        "projects/<str:pk>/interviews", interviews.list, name="project-interviews-list"
    ),
    path(
        "projects/<str:pk>/test_interviews",
        interviews.list_json,
        name="project-interviews-test-json",
    ),
    path("projects/<str:pk>/data", data.index, name="data"),
    path("data/<str:pk>/delete", data.delete_case, name="case-delete"),
    path("projects/<str:pk>/data/new", cases.new_case, name="case-new"),
    path("projects/<str:pk>/data/cases", data.cases, name="cases"),
    path("projects/<str:pk>/data/import", data.import_chats, name="import-chats"),
    path("projects/<str:pk>/themes", analysis.themes, name="themes"),
    path("projects/<str:pk>/query", analysis.themes, name="query"),
    path("projects/<str:pk>/harmonized", analysis.harmonized, name="harmonized"),
    path("case/<str:pk>", cases.index, name="case"),
    path("case/<str:pk>/new-followup", cases.new_followup, name="followup-new"),
    path("followup/<str:pk>/edit", cases.edit_followup, name="followup-edit"),
    path("api/projects/<str:pk>/all-cases", api.all_cases, name="api-all-cases"),
    path(
        "api/projects/<str:pk>/example", api.api_access_example, name="api-example-py"
    ),
]
