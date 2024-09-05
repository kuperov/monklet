import uuid
from typing import Dict

from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.timezone import now
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

import markdown

class Project(models.Model):
    class Meta:
        permissions = (("can_delete_own", "Can delete own project"),)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    research_aims = models.TextField(null=True, blank=True)
    funding = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now, null=False, editable=False)
    last_modified_at = models.DateTimeField(default=now, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')

    def can_view(self, user: User):
        if user == self.owner:
            return True
        return Member.objects.filter(project=self, user=user).exists()

    def can_edit(self, user: User):
        if user == self.owner:
            return True
        return Member.objects.filter(project=self, user=user, role='editor').exists()

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

    @property
    def url(self):
        return reverse_lazy('project', kwargs={'pk': self.id})

    @property
    def settings_url(self):
        return reverse_lazy('project-settings', kwargs={'pk': self.id})

    @property
    def delete_url(self):
        return reverse_lazy('project-delete', kwargs={'pk': self.id})

    @property
    def leave_url(self):
        return reverse_lazy('project-leave', kwargs={'pk': self.id})

    @property
    def members_url(self):
        return reverse_lazy('project-members', kwargs={'pk': self.id})

    @property
    def analysis_url(self):
        return reverse_lazy('project-analysis', kwargs={"pk": self.id})

    @property
    def questions_url(self):
        return reverse_lazy('project-questions', kwargs={"pk": self.id})

    @property
    def bots_url(self):
        return reverse_lazy('project-bots', kwargs={"pk": self.id})

    @property
    def invitations_url(self):
        return reverse_lazy('project-invitations', kwargs={"pk": self.id})

    @property
    def data_url(self):
        return reverse_lazy('project-responses', kwargs={"pk": self.id})

    @property
    def files_url(self):
        return reverse_lazy('project-files', kwargs={"pk": self.id})

    @property
    def consent_letters_url(self):
        return reverse_lazy('project-consent-letters', kwargs={"pk": self.id})


MEMBER_ROLES = [
    ('viewer', 'Viewer'),
    ('editor', 'Editor')
]

class Member(models.Model):
    """A member of a project.

    Created when an invitation is accepted, deleted when member is removed or leaves.
    """
    class Meta:
        indexes = [
            models.Index(fields=['project',]),
            models.Index(fields=['user',]),
        ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=6, choices=MEMBER_ROLES)
    last_modified_at = models.DateTimeField(null=False, blank=False, default=now)

    def __str__(self):
        return f"{self.name} ({self.role} on {self.project.name})"

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def avatar_url(self):
        try:
            return self.user.profile.avatar_url
        except ObjectDoesNotExist:
            settings.STATIC_URL + 'img/avatars/generic.svg'

    @property
    def email(self):
        return self.user.email

class Question(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="questions")
    question = models.TextField("Question")
    order = models.IntegerField("Order")
    is_enabled = models.BooleanField("Enabled", default=True, null=False)
    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return self.question


BOT_STATUS = [
    ('test', 'Testing'),
    ('live', 'Available'),
    ('disabled', 'Disabled')
]

class ConsentLetter(models.Model):
    id = models.UUIDField("Identifier", unique=True, primary_key=True, default=uuid.uuid4, null=False, editable=False)
    name = models.CharField("Short name", max_length=100, null=False, blank=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='consent_letters')
    short_md = models.TextField("Short version")
    letter_md = models.TextField("Letter")

    def __str__(self):
        return self.name


AI_MODELS = [
    ('gemini-flash-1.5', 'Gemini Flash 1.5')
]

BOT_STATUSES = [
    ('test', 'Testing'),
    ('live', 'Live'),
    ('disabled', 'Disabled')
]

def default_bot_config() -> Dict[str,str]:
    return {
        'temperature': 0.5,
        'top_p': 0.9,
        'top_k': 64,
        'max_output_tokens': 8192,
    }

class Bot(models.Model):
    id = models.UUIDField("Identifier", unique=True, primary_key=True, default=uuid.uuid4, null=False, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bots")
    name = models.CharField("Bot name", max_length=100)
    description = models.TextField("Description")
    version = models.CharField(default="1.0", max_length=10)
    prompt = models.TextField("Model prompt")
    aimodel = models.CharField("AI model", max_length=20, choices=AI_MODELS)
    config = models.JSONField("LLM options", default=default_bot_config)
    opening_user_statement = models.CharField("Opening user statement", default="Hello", max_length=100, blank=True, null=True)
    end_string = models.CharField("Termination string", max_length=100, default='ENDOFINTERVIEW')
    consent_letter = models.ForeignKey(ConsentLetter, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=BOT_STATUSES, default='test')
    allow_public = models.BooleanField("Allow public use", default=False, null=False)

    def __str__(self):
        return f"{self.name} ({self.version})"

    def test_interviews(self):
        return self.interviews.filter(status='test')


INTERVIEW_STATUS = [
    ('invited', 'Participant invited'),
    ('started', 'Started'),
    ('complete', 'Complete'),
    ('test', 'Test interview')
]

class Interview(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="interviews")
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE, related_name="interviews")
    subject_email = models.EmailField("Recipient email", blank=False, null=False)
    subject_name = models.CharField("Recipient name", max_length=50, blank=False, null=False)
    consent_letter = models.ForeignKey(ConsentLetter, on_delete=models.CASCADE)
    has_consented = models.BooleanField("Has given informed consent", default=False, blank=False, null=False)
    status = models.CharField(max_length=10, choices=INTERVIEW_STATUS, blank=False, null=False)
    created_at = models.DateTimeField(default=now, blank=False, null=False)
    started_at = models.DateTimeField("Time conversation started", blank=True, null=True)
    updated_at = models.DateTimeField("Last message at", blank=True, null=True)

    class Meta:
        ordering = ['subject_name']

    def __str__(self):
        return self.subject_name


SENDER_CHOICES = [
    ('ai', 'AI'),
    ('researcher', 'Researcher'),
    ('subject', 'Subject'),
]

class Message(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, null=False, blank=False, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES, blank=False, null=False)
    sent_at = models.DateTimeField("Sent at (server time)", default=now)
    message = models.TextField("Message text")

    class Meta:
        ordering = ['sent_at']

    def display(self) -> Dict[str, str]:
        """Convert to dict for rendering as JSON"""
        return {'message': self.message}

    def __str__(self):
        return f"{self.sender}: {self.message}"

class Dimension(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField("Dimension name", max_length=100)
    order = models.IntegerField("Order")

    def __str__(self):
        return f"Dimension {self.name} on {self.project}"

class InvitationEmail(models.Model):
    # redundant ref to project to make lookup simple
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='emails')
    sent_at = models.DateTimeField(default=now)
    email = models.EmailField()
    message = models.TextField()
    subject = models.CharField(max_length=200)

    def __str__(self):
        return "f{self.email} at {self.sent_at} for {self.project.name}"


class Transcript(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='transcripts')
    interview = models.ForeignKey(Interview, on_delete=models.SET_NULL, null=True, default=None)
    subject_name = models.CharField(max_length=100, blank=None)
    full_text = models.TextField()
    description = models.TextField()
    is_excluded = models.BooleanField("Exclude from analysis", default=False, null=False)
    created_at = models.DateTimeField(null=False, default=now)
    updated_at = models.DateTimeField(null=False, default=now)

    @property
    def transcript_type(self):
        return "Bot" if self.interview else "Manual"

    def __str__(self):
        return self.description
