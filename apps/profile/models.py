import hashlib

from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(default=now, null=False, editable=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    display = models.SmallIntegerField(default=1, choices=[(1, 'Light mode'),(2, 'Dark mode')])

    def __str__(self):
        return self.user.get_full_name()

    @property
    def avatar_url(self):
        # TODO: download and store gravatar as default on creation, otherwise generic.svg
        email = self.user.email
        email_hash = hashlib.md5(email.strip().lower().encode('utf-8')).hexdigest()
        return f"http://www.gravatar.com/avatar/{email_hash}"
        #return settings.STATIC_URL + 'img/avatars/generic.svg'

    @property
    def edit_url(self):
        return reverse_lazy('profile-edit', kwargs={'pk': self.pk})

    def all_projects(self):
        projects = []
        def details(proj):
            try:
                owner_avatar = proj.owner.profile.avatar_url
            except ObjectDoesNotExist:
                owner_avatar = settings.STATIC_URL + 'img/avatars/generic.svg'
            members = [{
                'name': proj.owner.get_full_name(),
                'avatar_url': owner_avatar}]
            for m in proj.members.all():
                members.append({
                    'name': m.name,
                    'avatar_url': m.avatar_url})
            return {
                'url': proj.url,
                'name': proj.name,
                'owner_name': proj.owner.get_full_name() or str(proj.owner),
                'last_modified_at': proj.last_modified_at,
                'members': members
            }
        for p in self.user.owned_projects.all():
            projects.append(details(p))
        for pm in self.user.project_memberships.select_related('project').all():
            projects.append(details(pm.project))
        sorted_projects = sorted(projects, key=lambda p: -p['last_modified_at'].timestamp())
        return sorted_projects
