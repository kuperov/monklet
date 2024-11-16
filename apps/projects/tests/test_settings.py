from django.urls import reverse
from django.core import mail
from apps.projects.tests.test_util import (
    create_interview_fixture,
    playwright_login,
)
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright


class ProjectViewTests(StaticLiveServerTestCase):

    def setUp(self):
        create_interview_fixture(self)

    def test_settings(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            playwright_login(self.live_server_url, page)
            settings_url = self.live_server_url + reverse(
                "project-settings", kwargs={"pk": self.project.pk}
            )
            page.goto(settings_url)
            page.get_by_role("tab").get_by_text("General").click()
            self.assertTrue(self.project.name in page.text_content("#settings-tab"))
            page.click("text=Edit")
            self.assertEqual(page.url, settings_url)
            self.assertTrue(page.locator("#id_research_aims").is_visible())
            page.click("text=Cancel")
            self.assertFalse(page.locator("#id_research_aims").is_visible())
            self.assertEqual(page.url, settings_url)
            page.fill("#id_name", "lorem ipsum")
            page.fill("#id_description", "dolor sit")
            page.fill("#id_research_aims", "amet")
            page.fill("#id_funding", "adiscur piscing")
            page.click("text=Save")
            self.assertEqual(
                page.get_by_role("alert").text_content(), "Project updated successfully"
            )
            self.assertTrue("lorem ipsum" in page.text_content("#settings-tab"))
            self.assertTrue("dolor sit" in page.text_content("#settings-tab"))

    def test_invite_members(self):
        with sync_playwright() as p:
            mail.outbox.clear()
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            playwright_login(self.live_server_url, page)
            settings_url = self.live_server_url + reverse(
                "project-settings", kwargs={"pk": self.project.pk}
            )
            page.goto(settings_url)
            page.get_by_role("tab").get_by_text("Members").click()
            tab_content = page.text_content("#members-tab")
            self.assertTrue(self.owner.name in tab_content)
            self.assertTrue(self.owner.email in tab_content)
            self.assertTrue("Owner" in tab_content)
            page.get_by_text("Invite new collaborator").click()
            self.assertTrue("Save" in page.text_content("#members-tab"))
            page.click("text=Cancel")
            self.assertTrue("Member name" in page.text_content("#members-tab"))
            page.get_by_text("Invite new collaborator").click()
            page.fill("#id_name", "Bob Smith")
            page.fill("#id_email", "bob@example.com")
            page.fill("#id_role", "editor")
            page.click("text=Save")
            self.assertEqual(
                page.text_content("role=alert"), "Invitation sent to bob@example.com"
            )
            # appears in sent invitations tab
            page.get_by_role("tab").get_by_text("Invitations sent").click()
            page.click("text=Refresh")
            self.assertTrue("Bob Smith" in page.content())
            # accept invitation flow (recipient)
            msg = mail.outbox.pop()
            # get link from msg
            collab_page = browser.new_page()
            # follow link in new browser
