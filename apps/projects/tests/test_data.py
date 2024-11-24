from django.test import TestCase
from apps.projects import models
from apps.projects.tests.test_util import (
    INTERVIEW_CONTENT,
    OWNER_EMAIL,
    OWNER_PASSWORD,
    create_ai_chat_fixture,
    acreate_ai_chat_fixture,
    create_interview_fixture,
    acreate_interview_fixture,
    aplaywright_login,
)

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from playwright.async_api import async_playwright


class TestImport(TestCase):

    def setUp(self):
        create_interview_fixture(self)
        self.client.login(email=OWNER_EMAIL, password=OWNER_PASSWORD)

    def test_create_transcript(self):
        ts = models.Case.from_chat(self.interview, pseudonym="Bob")
        self.assertEqual(ts.pseudonym, "Bob")
        self.assertEqual(ts.real_name, "Alex")
        rec = ts.current_records().first()
        self.assertEqual(len(rec.content), len(self.interview.content))
        pseudonymized_msg = INTERVIEW_CONTENT[0]["message"].replace("Alex", "Bob")
        self.assertEqual(rec.content[0]["text"], pseudonymized_msg)
        self.assertEqual(rec.content[0]["reference"], "00:00")


class TestMarkdown(TestCase):

    def setUp(self):
        create_ai_chat_fixture(self)
        self.note = models.Record.objects.create(
            project=self.project,
            case=self.case,
            record_type="note",
            content={"markdown": "lorem ipsum\n\ndolor sit amet"},
        )

    def test_generate_markdown(self):
        chat_md = self.chat.get_markdown()
        note_md = self.note.get_markdown()
        case_md = self.case.get_markdown()
        self.assertTrue(chat_md in case_md)
        self.assertTrue(note_md in case_md)
        self.assertTrue(case_md.startswith("# Case: Tony"))


class TestImportViews(StaticLiveServerTestCase):

    async def test_import_chat(self):
        await acreate_interview_fixture(self)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            await page.click("text=XYZ")
            self.assertEqual(
                page.url, f"{self.live_server_url}{self.project.get_absolute_url()}"
            )
            await page.locator(".menu-link").get_by_text("Data", exact=False).click()
            self.assertTrue("No data yet." in await page.text_content(".table"))
            await page.click("text=Import AI chats")
            await page.wait_for_load_state()
            # cancel goes back to empty data list
            await page.click("text=Cancel")
            await page.wait_for_load_state()
            self.assertTrue("No data yet." in await page.text_content(".table"))
            # go again but forget to import anything
            await page.click("text=Import AI chats")
            await page.wait_for_load_state()
            await page.fill("#id_form-0-pseudonym", "Harry")
            await page.click("text=Save")
            await page.wait_for_load_state()
            self.assertTrue(
                "Please select at least one interview"
                in await page.text_content(".errorlist")
            )
            # now select something to import
            await page.click("#id_form-0-selected")
            await page.click("text=Save")
            await page.wait_for_load_state()
            self.assertTrue(
                "Created 1 case(s), each with one transcript record"
                in await page.text_content("role=alert")
            )
            await page.click("text=Harry")
            await page.wait_for_load_state()
            await page.locator("a").get_by_text("[#1] AI chat").click()
            await page.wait_for_load_state()
            row_id = f"row-{INTERVIEW_CONTENT[0]['uuid']}"
            self.assertTrue(
                "Hello Harry, my name is Elsa." in await page.text_content(f"#{row_id}")
            )
            await page.locator(f"#{row_id}").locator(".dropdown-toggle").click()
            # await page.wait_for_load_state()
            await page.locator(f"#{row_id}").get_by_text(
                "Edit line", exact=False
            ).click()
            await page.wait_for_load_state()
            await page.fill("#id_text", "foo")
            await page.locator(f"#{row_id}").locator(".btn-primary").click()
            await page.wait_for_load_state()
            self.assertFalse(
                "Hello Harry, my name is Elsa." in await page.text_content(f"#{row_id}")
            )
            self.assertTrue("foo" in await page.text_content(f"#{row_id}"))
            await page.close()
            await browser.close()

    async def test_note(self):
        await acreate_ai_chat_fixture(self)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            await page.click("text=XYZ")
            await page.wait_for_load_state()
            await page.locator(".menu-link").get_by_text("Data", exact=False).click()
            await page.click("text=Tony")
            await page.wait_for_load_state()
            await page.get_by_text("New note", exact=False).click()
            await page.wait_for_load_state()
            await page.click("text=Cancel")
            self.assertEqual(
                "Case summary",
                (await page.locator("button.active").text_content()).strip(),
            )
            await page.wait_for_load_state()
            await page.get_by_text("New note", exact=False).click()
            await page.fill("#id_markdown", "Lorem ipsum\n\ndolor *sit* amet")
            await page.click("text=Save")
            await page.wait_for_load_state()
            self.assertEqual(
                (await page.get_by_role("alert").text_content()).strip(),
                "Record created",
            )
            await page.locator("a").get_by_text("[#2] Note", exact=False).click()
            # await page.wait_for_load_state()
            # panel_text = await page.locator('div.tab-pane.show').text_content()
            # self.assertTrue('dolor <i>sit</i> amet' in panel_text)
            await page.close()
            await browser.close()
