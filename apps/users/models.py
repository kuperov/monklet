from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Monklet.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = models.EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateField(default=now, null=False, editable=False)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    display = models.SmallIntegerField(
        default=1, choices=[(1, "Light mode"), (2, "Dark mode")]
    )

    def __str__(self):
        return f"{self.user.name} <{self.user.email}>"

    @property
    def avatar_url(self):
        # TODO: download and store gravatar as default on creation, otherwise generic.svg
        # email = self.user.email
        # email_hash = hashlib.md5(email.strip().lower().encode("utf-8")).hexdigest()
        # return f"//www.gravatar.com/avatar/{email_hash}"
        return settings.STATIC_URL + "img/avatars/generic.svg"

    def all_projects(self):
        projects = []

        def details(proj):
            try:
                owner_avatar = proj.owner.profile.avatar_url
            except ObjectDoesNotExist:
                owner_avatar = settings.STATIC_URL + "img/avatars/generic.svg"
            members = [{"name": proj.owner.name, "avatar_url": owner_avatar}]
            for m in proj.members.all():
                members.append({"name": m.name, "avatar_url": m.avatar_url})
            return {
                "pk": proj.pk,
                "url": proj.get_absolute_url(),
                "name": proj.name,
                "owner_name": proj.owner.name or str(proj.owner),
                "last_modified_at": proj.last_modified_at,
                "members": members,
                "owner_pk": proj.owner.pk,
            }

        for p in self.user.owned_projects.all():
            projects.append(details(p))
        for pm in self.user.project_memberships.select_related("project").all():
            projects.append(details(pm.project))
        sorted_projects = sorted(
            projects, key=lambda p: -p["last_modified_at"].timestamp()
        )
        return sorted_projects
