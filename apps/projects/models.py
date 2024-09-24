import uuid
from typing import Dict, Optional
import datetime

from django.db import models
from django.urls import reverse_lazy
from django.db.models import Count
from django.db.models.functions import TruncWeek, TruncDay

from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from docx import Document
import google.generativeai as genai

import markdown

from apps.projects.export import interview_doc
from apps.projects.util import datetime_str, format_timedelta, parse_datetime
from apps.users.models import User


class Project(models.Model):
    class Meta:
        permissions = (("can_delete_own", "Can delete own project"),)

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    research_aims = models.TextField(null=True, blank=True)
    funding = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=False, editable=False)
    last_modified_at = models.DateTimeField(auto_now=True, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_projects"
    )

    def can_view(self, user: User):
        if not user.is_authenticated:
            return False
        if user.pk == self.owner.pk:
            return True
        return Member.objects.filter(project=self, user=user).exists()

    def can_edit(self, user: User):
        if not user.is_authenticated:
            return False
        if user.pk == self.owner.pk:
            return True
        return Member.objects.filter(project=self, user=user, role="editor").exists()

    @property
    def member_count(self):
        return self.members.count() + 1  # include owner

    def is_member(self, user):
        if self.owner == user:
            return True
        return Member.objects.filter(project=self, user=user).exists()

    def __str__(self):
        return self.name

    def description_html(self):
        md = markdown.Markdown(extensions=["fenced_code"])
        return md.convert(self.description)

    def enabled_bots(self):
        return self.bots.exclude(status="disabled")

    def test_interviews(self):
        return self.interviews.filter(is_test=True, deleted_at=None)

    def invited_interviews(self):
        return self.interviews.filter(deleted_at=None, status="invited", is_test=False)

    def started_completed_interviews(self):
        return self.interviews.filter(deleted_at=None, is_test=False).exclude(
            status="invited"
        )

    def count_by_day(self):
        return (
            self.started_completed_interviews()
            .annotate(day_start=TruncDay("updated_at"))
            .values("day_start")
            .annotate(number=Count("id"))
            .order_by("day_start")
        )

    def count_by_week(self):
        return (
            self.started_completed_interviews()
            .annotate(week_start=TruncWeek("updated_at"))
            .values("week_start")
            .annotate(number=Count("id"))
            .order_by("week_start")
        )

    @property
    def url(self):
        return reverse_lazy("project", kwargs={"pk": self.id})

    @property
    def settings_url(self):
        return reverse_lazy("project-settings", kwargs={"pk": self.id})

    @property
    def delete_url(self):
        return reverse_lazy("project-delete", kwargs={"pk": self.id})

    @property
    def leave_url(self):
        return reverse_lazy("project-leave", kwargs={"pk": self.id})

    @property
    def members_url(self):
        return reverse_lazy("project-members", kwargs={"pk": self.id})

    @property
    def analysis_url(self):
        return reverse_lazy("project-analysis", kwargs={"pk": self.id})

    @property
    def questions_url(self):
        return reverse_lazy("project-questions", kwargs={"pk": self.id})

    @property
    def bots_url(self):
        return reverse_lazy("project-bots", kwargs={"pk": self.id})

    @property
    def invitations_url(self):
        return reverse_lazy("project-invitations", kwargs={"pk": self.id})

    @property
    def data_url(self):
        return reverse_lazy("project-responses", kwargs={"pk": self.id})

    @property
    def files_url(self):
        return reverse_lazy("project-files", kwargs={"pk": self.id})

    @property
    def consent_letters_url(self):
        return reverse_lazy("project-consent-letters", kwargs={"pk": self.id})


MEMBER_ROLES = [("viewer", "Viewer"), ("editor", "Editor")]


class Member(models.Model):
    """A member of a project.

    Created when an invitation is accepted, deleted when member is removed or leaves.
    """

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "project",
                ]
            ),
            models.Index(
                fields=[
                    "user",
                ]
            ),
        ]

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="members"
    )
    user = models.ForeignKey(
        User,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name="project_memberships",
    )
    role = models.CharField(max_length=6, choices=MEMBER_ROLES)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.role} on {self.project.name})"

    @property
    def name(self):
        return self.user.name

    @property
    def avatar_url(self):
        try:
            return self.user.profile.avatar_url
        except ObjectDoesNotExist:
            return settings.STATIC_URL + "img/avatars/generic.svg"

    @property
    def email(self):
        return self.user.email


class Question(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="questions"
    )
    question = models.TextField("Question")
    order = models.IntegerField("Order")
    is_enabled = models.BooleanField("Enabled", default=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return self.question


BOT_STATUS = [("test", "Testing"), ("live", "Available"), ("disabled", "Disabled")]


class ConsentLetter(models.Model):
    id = models.UUIDField(
        "Identifier",
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        null=False,
        editable=False,
    )
    name = models.CharField("Short name", max_length=100, null=False, blank=False)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="consent_letters"
    )
    short_md = models.TextField("Short version")
    letter_md = models.TextField("Letter")
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def short_html(self):
        md = markdown.Markdown(extensions=["fenced_code"])
        return md.convert(self.short_md)

    def letter_html(self):
        md = markdown.Markdown(extensions=["fenced_code"])
        return md.convert(self.letter_md)


AI_MODELS = [("gemini-1.5-flash", "Gemini Flash 1.5")]

BOT_STATUSES = [("test", "Testing"), ("live", "Live"), ("disabled", "Disabled")]


def default_bot_config() -> Dict[str, str]:
    return {
        "temperature": 0.9,
        "top_p": 0.9,
        "top_k": 64,
        "max_output_tokens": 8192,
    }


class Bot(models.Model):
    id = models.UUIDField(
        "Identifier",
        unique=True,
        primary_key=True,
        default=uuid.uuid4,
        null=False,
        editable=False,
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bots")
    name = models.CharField("Bot name", max_length=100)
    description = models.TextField("Description")
    version = models.CharField(default="1.0", max_length=10)
    prompt = models.TextField("Model prompt")
    caution = models.CharField(
        max_length=200, default="Please do not disclose sensitive information"
    )
    aimodel = models.CharField("AI model", max_length=20, choices=AI_MODELS)
    config = models.JSONField("LLM options", default=default_bot_config)
    opening_user_statement = models.CharField(
        "Opening user statement", default="Hello", max_length=100, blank=True, null=True
    )
    end_string = models.CharField(
        "Termination string", max_length=100, default="ENDOFINTERVIEW"
    )
    consent_letter = models.ForeignKey(
        ConsentLetter, on_delete=models.SET_NULL, null=True, blank=True
    )
    status = models.CharField(max_length=20, choices=BOT_STATUSES, default="test")
    allow_public = models.BooleanField("Allow public use", default=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.version})"

    def test_interviews(self):
        return self.interviews.filter(is_test=True, deleted_at=None)

    def actual_interviews(self):
        return self.interviews.filter(is_test=False, deleted_at=None)


INTERVIEW_STATUS = [
    ("invited", "Participant invited"),
    ("started", "Started"),
    ("complete", "Complete"),
]


class Interview(models.Model):
    id = models.UUIDField(
        "Identifier", primary_key=True, default=uuid.uuid4, blank=False, null=False
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="interviews"
    )
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="interviews")
    subject_email = models.EmailField("Recipient email", blank=True, null=False)
    subject_name = models.CharField(
        "Recipient name", max_length=50, blank=False, null=False
    )
    has_consented = models.BooleanField(
        "Has given informed consent", default=None, blank=True, null=True
    )
    followup_consented = models.BooleanField(
        "Has given consent for followup interview", default=None, blank=True, null=True
    )
    content = models.JSONField(
        "Interview content", default=list, blank=True, null=False
    )
    aimodel = models.CharField("AI model", max_length=20, choices=AI_MODELS)
    prompt = models.TextField("Model prompt", default=None, blank=True, null=True)
    config = models.JSONField("Model config", default=dict, blank=False, null=False)
    end_string = models.CharField(
        "Termination string", max_length=100, default="ENDOFINTERVIEW"
    )
    status = models.CharField(
        max_length=10, choices=INTERVIEW_STATUS, blank=False, null=False
    )
    attributes = models.JSONField(
        "Additional attributes", null=False, blank=False, default=dict
    )
    ip_address = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField("Started at", blank=True, null=True)
    updated_at = models.DateTimeField("Last modified", auto_now=True)
    deleted_at = models.DateTimeField("Deleted", blank=True, null=True)
    is_test = models.BooleanField(
        "This is a test interview", default=False, null=False, blank=False
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.bot.name} & {self.subject_name}"

    def last_message_text(self) -> str:
        if not self.content:
            return ""
        else:
            return self.content[-1].get("message")

    async def start_async(self):
        """Generate prompt and config, create initial message, post greeting from model"""
        # this should be the only time we look up the bot in the course of the chat
        # (apart from rendering the chat page)
        if self.status != "invited":
            raise Exception(f"Interview is {self.status}")
        try:
            self.status = "started"
            bot = await Bot.objects.aget(pk=self.bot_id)
            # generate and store prompt, config, end_string
            # keeping these values avoids issues with bot getting updated
            self.prompt = bot.prompt.format(SUBJECT_NAME=self.subject_name)
            self.aimodel = bot.aimodel
            self.end_string = bot.end_string
            generation_config = default_bot_config()
            generation_config.update(
                {k: bot.config[k] for k in generation_config.keys() if k in bot.config}
            )
            self.config = generation_config
            # set up ai model
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name=self.aimodel,
                generation_config=self.config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction=self.prompt,
            )
            chat_session = model.start_chat(history=[])
            response = await chat_session.send_message_async(
                bot.opening_user_statement or "Hello"
            )
            response_dict = {
                "uuid": str(uuid.uuid4),
                "sender": "model",
                "message": response.text.strip(),
                "sent_at": datetime_str(now()),
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "total_token_count": response.usage_metadata.total_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
            }
            self.content.append(response_dict)
        except Exception as ex:  # noqa: E722
            response_dict = {
                "sender": "System",
                "message": "An error occurred.",
                "sent_at": datetime_str(now()),
            }
            self.content.append(response_dict)
            import traceback

            traceback.print_exception(ex)
        await self.asave()
        return response_dict

    async def add_user_message_async(self, message: str):
        if self.content is None:
            self.content = []  # shouldn't happen?
        if self.status == "complete":
            raise Exception("Interview is complete")
        self.content.append(
            dict(
                uuid=str(uuid.uuid4()),
                sender="user",
                message=message,
                sent_at=datetime_str(now()),
            )
        )
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel(
                model_name=self.aimodel,
                generation_config=self.config,
                # safety_settings = Adjust safety settings
                # See https://ai.google.dev/gemini-api/docs/safety-settings
                system_instruction=self.prompt,
            )
            chat_session = model.start_chat(
                history=[
                    {"role": h["sender"], "parts": [h["message"]]}
                    for h in self.content
                    if h["sender"] in ["user", "model"]
                ]
            )
            response = await chat_session.send_message_async(message)
            message = response.text.strip()
            if self.end_string in message:
                message = message.replace(self.end_string, "")
                self.status = "complete"
            response_dict = {
                "uuid": str(uuid.uuid4()),
                "sender": "model",
                "message": message.strip(),
                "sent_at": datetime_str(now()),
                "prompt_token_count": response.usage_metadata.prompt_token_count,
                "total_token_count": response.usage_metadata.total_token_count,
                "candidates_token_count": response.usage_metadata.candidates_token_count,
            }
            self.content.append(response_dict)
        except Exception as ex:  # noqa: E722
            response_dict = {
                "uuid": (uuid.uuid4()),
                "sender": "System",
                "message": "An error occurred.",
                "sent_at": datetime_str(now()),
            }
            self.content.append(response_dict)
            import traceback

            traceback.print_exception(ex)
        await self.asave()
        return response_dict

    def send_invitation_email(self, request):
        """Render and send invitation email.

        Side effect: updates and saves model object.
        The request is required to obtain a complete landing
        URL, which is different per environment.
        """
        landing_url = request.build_absolute_uri(
            reverse_lazy("interview-landing", kwargs={"pk": self.pk})
        )
        ctx = {
            "request": request,
            "user": request.user,
            "subject_name": self.subject_name,
            "subject_email": self.subject_email,
            "project": self.project,
            "bot": self.bot,
            "expiry_days": settings.INVITATION_EXPIRY_DAYS,
            "landing_url": landing_url,
        }
        self.message = render_to_string("interviews/interview_email.html", ctx)
        plain = strip_tags(self.message)
        self.subject = f"Invitation: {self.project.name}"
        result = mail.send_mail(
            subject=self.subject,
            message=plain,
            from_email=settings.EMAIL_SENDER,
            recipient_list=[f"{self.subject_name} <{self.subject_email}>"],
            html_message=self.message,
            fail_silently=True,
        )
        if result:
            self.sent_at = now()
        self.save()
        return result

    def messages_list(self):
        msg_list = []
        if self.content and isinstance(self.content, list):
            start_at = parse_datetime(self.content[0].get("sent_at"))
            name_map = {
                "system": "System",
                "user": self.subject_name,
                "model": self.bot.name,
            }

            def format(msg):
                sent_at = parse_datetime(msg["sent_at"])
                if isinstance(sent_at, datetime.datetime) and isinstance(
                    start_at, datetime.datetime
                ):
                    delta = sent_at - start_at
                    time_fmt = format_timedelta(delta)
                else:
                    time_fmt = ""
                return {
                    "message": msg["message"],
                    "sender": name_map.get(msg["sender"]),
                    "time": time_fmt,
                }

            msg_list = [format(msg) for msg in self.content]
        return msg_list

    def total_duration(self) -> Optional[datetime.timedelta]:
        """Time from first to last message. Null if can't be computed."""
        if not self.content or not isinstance(self.content, list):
            return None
        start_at = parse_datetime(self.content[0].get("sent_at"))
        end_at = parse_datetime(self.content[-1].get("sent_at"))
        if not start_at or not end_at or start_at == end_at:
            return None
        return end_at - start_at

    def total_token_usage(self):
        """Sum up token usage for this interview.

        Returns:
            tuple of (prompt_tokens, gen_tokens, total_tokens)
        """
        prompt_tokens = gen_tokens = total_tokens = 0
        if self.content and isinstance(self.config, list):
            for msg in self.content:
                if not isinstance(msg, dict):
                    continue
                prompt_tokens += msg.get("prompt_token_count", 0)
                gen_tokens += msg.get("candidates_token_count", 0)
                total_tokens += msg.get("total_token_count", 0)
        return prompt_tokens, gen_tokens, total_tokens

    def as_docx(self, include_metadata: bool = True) -> Document:  # noqa: F821
        """Construct docx.Document summarizing the interviw

        Args:
            include_metadata (bool, optional): Include metadata. Defaults to True.

        Returns:
            Document: Document representation
        """
        messages = self.messages_list()
        dur = self.total_duration()
        prompt_tokens, gen_tokens, total_tokens = self.total_token_usage()
        metadata = None
        if include_metadata:
            metadata = {
                "Subject name": self.subject_name,
                "Subject email": self.subject_email,
                "Interview status": self.status.title(),
                "Total duration": format_timedelta(dur) if dur else None,
                "Participation consent": "Yes" if self.has_consented else "No",
                "Follow-up consent": "Yes" if self.followup_consented else "No",
                "Bot": self.bot.name,
                "Model": self.aimodel,
                "Model tokens consumed": f"{total_tokens} ({prompt_tokens} prompt, {gen_tokens} output)",
                "Created": f"{self.created_at: %Y-%m-%d %H:%M} UTC",
                "Last updated": f"{self.updated_at: %Y-%m-%d %H:%M} UTC",
            }
        title = f"{self.subject_name} & {self.bot.name}"
        return interview_doc(title, messages, metadata)


# DIM_TYPE_CHOICES = [
#     ('char', 'Character'),
#     ('int', 'Integer'),
#     ('choice', 'Choice')
# ]


class Dimension(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField("Dimension name", max_length=100)
    order = models.IntegerField("Order")
    # dimtype = models.CharField("Type", max_length=10, choices=DIM_TYPE_CHOICES, null=False, blank=False)
    # dimspec = models.JSONField(default=dict, blank=False)

    def __str__(self):
        return f"Dimension {self.name} on {self.project}"


class InvitationEmail(models.Model):
    # redundant ref to project to make lookup simple
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    interview = models.ForeignKey(
        Interview, on_delete=models.CASCADE, related_name="emails"
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()
    message = models.TextField()
    subject = models.CharField(max_length=200)

    def __str__(self):
        return "f{self.email} at {self.sent_at} for {self.project.name}"


class Transcript(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="transcripts"
    )
    interview = models.ForeignKey(
        Interview, on_delete=models.SET_NULL, null=True, default=None
    )
    subject_name = models.CharField(max_length=100, blank=None)
    full_text = models.TextField()
    description = models.TextField()
    is_excluded = models.BooleanField(
        "Exclude from analysis", default=False, null=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    @property
    def transcript_type(self):
        return "Bot" if self.interview else "Manual"

    def __str__(self):
        return self.description


class MemberInvitation(models.Model):
    """An email sent to a potential collaborator. One-to-many with Member.

    Links expire after `expires_at`, which is updated to `now()` if revoked.
    """

    class Meta:
        ordering = ["-created_at"]

    def default_expiry():
        return now() + datetime.timedelta(days=settings.INVITATION_EXPIRY_DAYS)

    code = models.UUIDField(
        default=uuid.uuid4, primary_key=True, editable=False, unique=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="member_invitations",
    )
    role = models.CharField(max_length=6, blank=False, null=False, choices=MEMBER_ROLES)
    email = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=False, blank=False, default=default_expiry)
    # email address of user that accepted this invitation, initially null
    accepted_email = models.CharField(max_length=100, blank=True, null=True)

    @property
    def landing_url(self):
        return reverse_lazy("invitation-landing", kwargs={"code": self.pk})

    def accept(self, user) -> Member:
        """Accept the invitation and marks it expired so it can't be used again."""
        self.accepted_email = user.email
        self.expire()  # saves
        return Member.objects.create(project=self.project, user=user, role=self.role)

    def expire(self) -> None:
        """Marks this invitation as expired.

        Raises an exception if the invitation has already been accepted.
        """
        if self.expires_at > now():
            self.expires_at = now()
            self.save()

    @property
    def is_valid(self) -> bool:
        return self.sent_at is not None and not self.is_expired

    @property
    def is_expired(self) -> bool:
        return self.expires_at <= now()

    @property
    def status(self) -> str:
        if self.accepted_email:
            return "Accepted"
        elif self.is_expired:
            return "Expired"
        elif self.is_valid:
            return "Valid"
        elif self.sent_at is None:
            return "Not sent"
        else:
            return "Invalid"

    def __str__(self):
        return f"{self.name} <{self.email}> {self.status}"

    def send_email(self, request) -> int:
        """Render and send invitation email.

        Side effect: updates and saves model object.
        The request is required to obtain a complete landing
        URL, which is different per environment.
        """
        ctx = {
            "request": request,
            "user": request.user,
            "name": self.name,
            "project_name": self.project.name,
            "expiry_days": settings.INVITATION_EXPIRY_DAYS,
            "landing_url": request.build_absolute_uri(self.landing_url),
        }
        self.message = render_to_string("invitations/member_email.html", ctx)
        plain = strip_tags(self.message)
        self.subject = f"Invitation to collaborate: {self.project.name}"
        result = mail.send_mail(
            subject=self.subject,
            message=plain,
            from_email=settings.EMAIL_SENDER,
            recipient_list=[f"{self.name} <{self.email}>"],
            html_message=self.message,
            fail_silently=True,
        )
        if result:
            self.sent_at = now()
        self.save()
        return result

    def resend_email(self, request) -> int:
        """Resend invitation by expiring this one and issuing another."""
        inv = MemberInvitation.objects.create(
            project=self.project, email=self.email, name=self.name, role=self.role
        )
        inv.send_email(request)  # regenerates email content from template
        self.expire()
