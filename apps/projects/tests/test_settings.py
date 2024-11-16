from django.urls import reverse
from django.core import mail
from apps.projects.tests.test_util import (
    acreate_interview_fixture,
    aplaywright_login,
)
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.async_api import async_playwright
from apps.projects import models


class ProjectViewTests(StaticLiveServerTestCase):

    async def test_settings(self):
        await acreate_interview_fixture(self)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            settings_url = self.live_server_url + reverse(
                "project-settings", kwargs={"pk": self.project.pk}
            )
            await page.goto(settings_url)
            await page.get_by_role("tab").get_by_text("General").click()
            self.assertTrue(
                self.project.name in await page.text_content("#settings-tab")
            )
            await page.click("text=Edit")
            self.assertEqual(page.url, settings_url)
            self.assertTrue(await page.locator("#id_research_aims").is_visible())
            # cancel goes back to readonly page
            await page.click("text=Cancel")
            self.assertFalse(await page.locator("#id_research_aims").is_visible())
            # edit settings
            await page.click("text=Edit")
            await page.fill("#id_name", "lorem ipsum")
            await page.fill("#id_description", "dolor sit")
            await page.fill("#id_research_aims", "amet")
            await page.fill("#id_funding", "adiscur piscing")
            await page.click("text=Save")
            self.assertEqual(
                (await page.get_by_role("alert").text_content()).strip(),
                "Project updated successfully",
            )
            self.assertTrue("lorem ipsum" in await page.text_content("#settings-tab"))
            self.assertTrue("dolor sit" in await page.text_content("#settings-tab"))

    async def test_invite_members(self):
        await acreate_interview_fixture(self)
        async with async_playwright() as p:
            mail.outbox.clear()
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            settings_url = self.live_server_url + reverse(
                "project-settings", kwargs={"pk": self.project.pk}
            )
            await page.goto(settings_url)
            await page.get_by_role("tab").get_by_text("Members").click()
            tab_content = await page.text_content("#members-tab")
            self.assertTrue(self.owner.name in tab_content)
            self.assertTrue(self.owner.email in tab_content)
            self.assertTrue("Owner" in tab_content)
            await page.get_by_text("Invite new collaborator").click()
            await page.wait_for_load_state()
            self.assertTrue(await page.locator("#id_name").is_visible())
            # cancel goes back to member list
            await page.click("text=Cancel")
            await page.wait_for_load_state()
            self.assertTrue("Member name" in await page.text_content("#members-tab"))
            # send invitation
            await page.get_by_text("Invite new collaborator").click()
            await page.fill("#id_name", "Bob Smith")
            await page.fill("#id_email", "bob@example.com")
            await page.select_option("#id_role", "editor")
            await page.click("text=Save")
            self.assertEqual(
                (await page.text_content("role=alert")).strip(),
                "Invitation sent to bob@example.com",
            )
            # Bob Smith appears in sent invitations tab
            await page.get_by_role("tab").get_by_text("Invitations sent").click()
            await page.wait_for_load_state()
            await page.locator("#invitations-tab").get_by_text(
                "Refresh", exact=False
            ).click()
            await page.wait_for_load_state()
            self.assertTrue("Bob Smith" in await page.content())
            await page.get_by_role("tab").get_by_text("Members").click()
            await page.wait_for_load_state()
            # accept invitation flow (recipient)
            msg = mail.outbox.pop()
            # check link is in message, then follow it
            # (we don't extract link to avoid confusion with e.g. image assets)
            inv = await models.MemberInvitation.objects.aget(email="bob@example.com")
            landing_url = self.live_server_url + inv.landing_url
            self.assertTrue(landing_url in msg.body)

            collab_browser = await p.chromium.launch(headless=True)
            collab_page = await collab_browser.new_page()
            # follow link and sign up in new browser
            await collab_page.goto(landing_url)
            await collab_page.click("text=Sign up")
            await collab_page.fill("#id_name", "Bob Smith")
            await collab_page.fill("#id_email", "bob@example.com")
            await collab_page.fill("#id_password1", "tiger_tiger")
            await collab_page.fill("#id_password2", "tiger_tiger")
            await collab_page.click("text=Sign up")
            await collab_page.click("text=Yes, accept")
            # should now see dashboard
            self.assertEqual(
                collab_page.url, self.live_server_url + self.project.get_absolute_url()
            )
            await collab_page.close()
            await collab_browser.close()
            # refreshed user list shows Bob Smith
            await page.locator("#members-tab").get_by_text(
                "Refresh", exact=False
            ).click()
            await page.wait_for_load_state()
            self.assertTrue("Bob Smith" in await page.content())
            await page.close()
            await browser.close()
