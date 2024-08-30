import uuid
from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.timezone import now

import markdown

class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    research_aims = models.TextField(null=True, blank=True)
    funding = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now, null=False, editable=False)
    last_modified_at = models.DateTimeField(default=now, null=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

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

    def url(self):
        return reverse_lazy('project', kwargs={'pk': self.id})

    def settings_url(self):
        return reverse_lazy('project-settings', kwargs={'pk': self.id})

    def delete_url(self):
        return reverse_lazy('project-delete', kwargs={'pk': self.id})

    def leave_url(self):
        return reverse_lazy('project-leave', kwargs={'pk': self.id})

    def members_url(self):
        return reverse_lazy('project-members', kwargs={'pk': self.id})

    def data_url(self):
        return reverse_lazy('project-data', kwargs={"pk": self.id})

    def analysis_url(self):
        return reverse_lazy('project-analysis', kwargs={"pk": self.id})

    def questions_url(self):
        return reverse_lazy('project-questions', kwargs={"pk": self.id})

    def bots_url(self):
        return reverse_lazy('project-bots', kwargs={"pk": self.id})

    def invitations_url(self):
        return reverse_lazy('project-invitations', kwargs={"pk": self.id})

    def responses_url(self):
        return reverse_lazy('project-responses', kwargs={"pk": self.id})

    def files_url(self):
        return reverse_lazy('project-files', kwargs={"pk": self.id})


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
    user = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE, related_name='projects')
    role = models.CharField(max_length=6, choices=MEMBER_ROLES)
    last_modified_at = models.DateTimeField(null=False, blank=False, default=now)

    def __str__(self):
        return f"{self.name} ({self.role} on {self.project.name})"

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def avatar_url(self):
        return self.user.profile.avatar_url

    @property
    def email(self):
        return self.user.email
