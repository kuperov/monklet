from asgiref.sync import sync_to_async
from django.urls import reverse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.async_api import async_playwright

from apps.projects.tests.test_util import aplaywright_login, acreate_interview_fixture
from apps.users.models import User
from apps.projects import models


class CreateProjectViewTests(StaticLiveServerTestCase):

    async def test_create_project(self):
        self.owner = await sync_to_async(User.objects.create_user)(
            email="a@b.com", password="secret"
        )
        self.assertFalse(
            await models.Project.objects.filter(name="The project").aexists()
        )
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            self.assertEqual(page.url, f"{self.live_server_url}/users/profile")
            # cancel
            await page.click("text=New Project")
            self.assertEqual(page.url, f"{self.live_server_url}/projects/new")
            await page.click("text=Cancel")
            self.assertEqual(page.url, f"{self.live_server_url}/users/profile")
            # save
            await page.click("text=New Project")
            self.assertTrue("New project" in await page.title())
            self.assertEqual(page.url, f"{self.live_server_url}/projects/new")
            await page.fill("#id_name", "The project")
            await page.fill("#id_description", "'The project' is a test project")
            await page.click("text=Save")
            proj = await models.Project.objects.aget(name="The project")
            self.assertEqual(proj.description, "'The project' is a test project")
            self.assertEqual(
                page.url, f"{self.live_server_url}{proj.get_absolute_url()}"
            )
            await page.close()
            await browser.close()


class ProjectViewTests(StaticLiveServerTestCase):

    async def test_leave_project(self):
        await acreate_interview_fixture(self)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await aplaywright_login(self.live_server_url, page)
            await page.goto(f"{self.live_server_url}{reverse('users:profile')}")
            await page.locator(".ri-more-2-line").click()
            await page.click("text=Project settings")
            self.assertEqual(
                page.url,
                f"{self.live_server_url}{reverse('project-settings', kwargs={'pk': self.project.pk})}",
            )
            await page.go_back()
            await page.locator(".ri-more-2-line").click()
            await page.click("text=Delete project")
            self.assertEqual("Delete project XYZ?", await page.text_content(".card h6"))
            # cancel
            await page.click("text=Don't delete")
            self.assertEqual(
                page.url, f"{self.live_server_url}{reverse('users:profile')}"
            )
            await page.go_back()
            # delete
            await page.click("text=Yes, delete")
            self.assertEqual(
                page.url, f"{self.live_server_url}{reverse('users:profile')}"
            )
            self.assertEqual(
                "Project XYZ deleted.", (await page.text_content(".alert")).strip()
            )
            # check mark deletion
            proj = await models.Project.objects.aget(pk=self.project.pk)
            self.assertIsNotNone(proj.deleted_at)
