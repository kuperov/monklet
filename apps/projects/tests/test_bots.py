from django.urls import reverse
from apps.projects.tests.test_util import (
    create_project_fixture,
    playwright_login,
)
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright
from apps.projects import models


class ProjectViewTests(StaticLiveServerTestCase):

    def setUp(self):
        create_project_fixture(self)

    def test_settings(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            playwright_login(self.live_server_url, page)
            bots_url = self.live_server_url + reverse(
                "project-bots", kwargs={"pk": self.project.pk}
            )
            page.goto(self.live_server_url + self.project.get_absolute_url())
            page.locator(".menu-link").get_by_text("Bots").click()
            self.assertEqual(bots_url, page.url)
            page.locator(".btn-primary").get_by_text("New Bot").click()
            page.fill("#id_name", "Bob")
            page.fill("#id_description", "Silly bot")
            page.fill(
                "#id_prompt",
                "You are a silly chatbot. Conduct a conversation where you tell jokes.  When the conversation is over, output ENDOFCHAT.",
            )
            page.fill("#id_aimodel", "gemini-1.5-flash")
            page.fill("#id_end_string", "ENDOFCHAT")
            page.click("text=Save")
            self.assertTrue(models.Bot.objects.filter(name="Bob").exists())
