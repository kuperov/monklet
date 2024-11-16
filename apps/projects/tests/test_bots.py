from django.urls import reverse
from apps.projects.tests.test_util import (
    acreate_project_fixture,
    aplaywright_login,
)
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.async_api import async_playwright
from apps.projects import models


class ProjectViewTests(StaticLiveServerTestCase):

    async def test_create_bot(self):
        await acreate_project_fixture(self)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            bots_url = self.live_server_url + reverse(
                "project-bots", kwargs={"pk": self.project.pk}
            )
            await page.goto(self.live_server_url + self.project.get_absolute_url())
            await page.locator(".menu-link").get_by_text("Bots").click()
            self.assertEqual(bots_url, page.url)
            await page.locator(".btn-primary").get_by_text("New Bot").click()
            # cancel hides form
            await page.click("text=Cancel")
            self.assertFalse(await page.locator("#id_name").is_visible())
            # create bot
            await page.locator(".btn-primary").get_by_text("New Bot").click()
            await page.fill("#id_name", "Bob")
            await page.fill("#id_description", "Silly bot")
            await page.fill(
                "#id_prompt",
                "You are a silly chatbot. Conduct a conversation where you tell jokes.  When the conversation is over, output ENDOFCHAT.",
            )
            await page.select_option("#id_aimodel", "Gemini Flash 1.5")
            await page.fill("#id_end_string", "ENDOFCHAT")
            await page.locator("input").get_by_text("Save").click()
            self.assertTrue("Bot created" in await page.text_content("role=alert"))
            self.assertTrue(await models.Bot.objects.filter(name="Bob").aexists())
            await page.close()
            await browser.close()

    async def test_edit_bot(self):
        await acreate_project_fixture(self)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            bots_url = self.live_server_url + reverse(
                "project-bots", kwargs={"pk": self.project.pk}
            )
            await page.goto(bots_url)
            await page.locator("button").locator(".ri-more-2-line").click()
            await page.locator(".ri-edit-line").click()
            self.assertTrue(await page.locator("#id_name").is_visible())
            await page.fill("#id_name", "qwerty")
            await page.click("text=Save")
            self.assertEqual(
                "Updated bot", (await page.text_content("role=alert")).strip()
            )
            self.assertTrue("qwerty" in await page.content())
            await page.close()
            await browser.close()
