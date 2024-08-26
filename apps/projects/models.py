import uuid
from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.timezone import now

import markdown


class ProjectManager(models.Manager):
    def create(self, *args, **kwargs):
        owner = kwargs['owner']
        if owner not in kwargs['members']:
            kwargs['members'] = kwargs.get('members', []) + [owner]
        return super().create(*args, **kwargs)


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50, null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    research_aims = models.TextField(null=True, blank=True)
    funding = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=now, null=False, editable=False)
    last_modified_at = models.DateTimeField(default=now, null=False, editable=False)
    deleted_at = models.DateField(null=True, blank=True, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name='project_memberships')

    # TODO: on create, add owner to members

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
