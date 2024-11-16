from django.test import TestCase
from apps.projects import models
from apps.projects.tests.test_util import (
    INTERVIEW_CONTENT,
    OWNER_EMAIL,
    OWNER_PASSWORD,
    create_interview_fixture,
    playwright_login,
)

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from playwright.sync_api import sync_playwright


class TestImport(TestCase):

    def setUp(self):
        create_interview_fixture(self)
        self.client.login(email=OWNER_EMAIL, password=OWNER_PASSWORD)

    def test_create_transcript(self):
        ts = models.Transcript.from_chat(self.interview, "Bob")
        self.assertEqual(len(ts.content), len(self.interview.content))
        self.assertEqual(ts.content[0]["text"], INTERVIEW_CONTENT[0]["message"])
        self.assertEqual(ts.content[0]["reference"], "00:00")
        self.assertEqual(str(ts), "Transcript: Bob")


class TestImportViews(StaticLiveServerTestCase):

    def setUp(self):
        create_interview_fixture(self)

    def test_import_transcript(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            playwright_login(self.live_server_url, page)
            page.click("text=XYZ")
            self.assertEqual(
                page.url, f"{self.live_server_url}{self.project.get_absolute_url()}"
            )
