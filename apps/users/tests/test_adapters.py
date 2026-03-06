from django.test import TestCase, override_settings

from apps.users.adapters import AccountAdapter, SocialAccountAdapter


class AccountAdapterTests(TestCase):
    @override_settings(ACCOUNT_ALLOW_REGISTRATION=True)
    def test_account_adapter_allows_signup_when_enabled(self):
        adapter = AccountAdapter()
        self.assertTrue(adapter.is_open_for_signup(request=None))

    @override_settings(ACCOUNT_ALLOW_REGISTRATION=False)
    def test_account_adapter_blocks_signup_when_disabled(self):
        adapter = AccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(request=None))


class SocialAccountAdapterTests(TestCase):
    @override_settings(ACCOUNT_ALLOW_REGISTRATION=True)
    def test_social_adapter_allows_signup_when_enabled(self):
        adapter = SocialAccountAdapter()
        self.assertTrue(adapter.is_open_for_signup(request=None, sociallogin=None))

    @override_settings(ACCOUNT_ALLOW_REGISTRATION=False)
    def test_social_adapter_blocks_signup_when_disabled(self):
        adapter = SocialAccountAdapter()
        self.assertFalse(adapter.is_open_for_signup(request=None, sociallogin=None))

