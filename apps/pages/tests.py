from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

import logging


class ErrorPageTestCase(TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.previous_level = self.logger.getEffectiveLevel()
        self.logger.setLevel(level=logging.CRITICAL)

    def tearDown(self):
        self.logger.setLevel(self.previous_level)

    def test_errors(self):
        resp = self.client.get("/urldoesntexist")
        self.assertContains(resp, "Not Found", status_code=404)
        resp = self.client.get("/404", follow=True)
        self.assertContains(resp, "Not Found", status_code=404)
        resp = self.client.get("/401", follow=True)
        self.assertContains(resp, "Unauthorized", status_code=401)
        resp = self.client.get("/403", follow=True)
        self.assertContains(resp, "Forbidden", status_code=403)
        resp = self.client.get("/400", follow=True)
        self.assertContains(resp, "Bad Request", status_code=400)
        resp = self.client.get("/500", follow=True)
        self.assertContains(resp, "Internal Server Error", status_code=500)


class FrontPagesTestCase(TestCase):

    def test_homepage_for_anonymous_user(self):
        resp = self.client.get("/")
        self.assertContains(resp, "Monklet: open-source AI interviewing", status_code=200)
        self.assertContains(resp, "run chat-based interviews and analyze qualitative data")
        self.assertContains(resp, reverse_lazy("account_login"))
        self.assertContains(resp, reverse_lazy("account_signup"))

    def test_homepage_redirects_authenticated_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            email="user@example.com",
            password="test-password",
        )
        self.client.force_login(user)
        resp = self.client.get("/")
        self.assertRedirects(resp, reverse_lazy("users:profile"))
