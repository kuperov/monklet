import datetime
import uuid

from django.db import models
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.conf import settings
from django.core import mail
from django.contrib.auth import get_user_model
User = get_user_model()
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from apps.projects.models import Project, Member, MEMBER_ROLES

class MemberInvitation(models.Model):
    """An email sent to a potential collaborator. One-to-many with Member.

    Links expire after `expires_at`, which is updated to `now()` if revoked.
    """
    class Meta:
        ordering = ['-created_at']

    def default_expiry():
        return now() + datetime.timedelta(days=settings.INVITATION_EXPIRY_DAYS)

    code = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=False, null=False, related_name='member_invitations')
    role = models.CharField(max_length=6, blank=False, null=False, choices=MEMBER_ROLES)
    email = models.CharField(max_length=100, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    message = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(null=False, blank=False, default=now)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=False, blank=False, default=default_expiry)
    # email address of user that accepted this invitation, initially null
    accepted_email = models.CharField(max_length=100, blank=True, null=True)

    @property
    def landing_url(self):
        return reverse_lazy('invitation-landing', kwargs = {'code': self.pk})

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
            return 'Accepted'
        elif self.is_expired:
            return 'Expired'
        elif self.is_valid:
            return 'Valid'
        elif self.sent_at is None:
            return 'Not sent'
        else:
            return 'Invalid'

    def send_email(self, request) -> int:
        """Render and send invitation email.

        Side effect: updates and saves model object.
        The request is required to obtain a complete landing
        URL, which is different per environment.
        """
        ctx = {
            'name': self.name,
            'project_name': self.project.name,
            'landing_url': request.build_absolute_uri(self.landing_url)
        }
        self.message = render_to_string('invitations/member_email.html', ctx)
        plain = strip_tags(self.message)
        self.subject = f"Collaborate on {self.project.name}"
        result = mail.send_mail(
            subject=self.subject,
            message=plain,
            from_email=settings.EMAIL_SENDER,
            recipient_list=[self.email],
            html_message=self.message,
            fail_silently=True
        )
        if result:
            self.sent_at = now()
        self.save()
        return result

    def resend_email(self, request) -> int:
        """Resend invitation by expiring this one and issuing another."""
        inv = MemberInvitation.objects.create(
            project=self.project,
            email=self.email,
            name=self.name,
            message_markdown=self.message_markdown
        )
        inv.send_email()
        self.expire()
