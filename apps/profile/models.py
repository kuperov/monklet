import hashlib

from django.db import models
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.utils.timezone import now


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
