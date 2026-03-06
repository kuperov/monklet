from django.conf import settings

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


def _registration_allowed() -> bool:
    return bool(getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True))


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return _registration_allowed()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return _registration_allowed()

