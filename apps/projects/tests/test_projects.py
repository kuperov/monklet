from django.urls import reverse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright.sync_api import sync_playwright

from apps.projects.tests.test_util import create_interview_fixture, playwright_login
from apps.users.models import User
from apps.projects import models


class CreateProjectViewTests(StaticLiveServerTestCase):

    def setUp(self):
        self.owner = User.objects.create_user(email="a@b.com", password="secret")

    def test_create_project(self):
        self.assertFalse(models.Project.objects.filter(name="The project").exists())
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            playwright_login(self.live_server_url, page)
            self.assertEqual(page.url, f"{self.live_server_url}/users/profile")
            # cancel
            page.click("text=New Project")
            self.assertEqual(page.url, f"{self.live_server_url}/projects/new")
            page.click("text=Cancel")
            self.assertEqual(page.url, f"{self.live_server_url}/users/profile")
            # save
            page.click("text=New Project")
            self.assertTrue("New project" in page.title())
            self.assertEqual(page.url, f"{self.live_server_url}/projects/new")
            page.fill("#id_name", "The project")
            page.fill("#id_description", "'The project' is a test project")
            page.click("text=Save")
            proj = models.Project.objects.get(name="The project")
            self.assertEqual(proj.description, "'The project' is a test project")
            self.assertEqual(
                page.url, f"{self.live_server_url}{proj.get_absolute_url()}"
            )
            page.close()


class ProjectViewTests(StaticLiveServerTestCase):

    def setUp(self):
        create_interview_fixture(self)

    def test_leave_project(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            playwright_login(self.live_server_url, page)
            page.goto(f"{self.live_server_url}{reverse('users:profile')}")
            page.locator(".ri-more-2-line").click()
            page.click("text=Project settings")
            self.assertEqual(
                page.url,
                f"{self.live_server_url}{reverse('project-settings', kwargs={'pk': self.project.pk})}",
            )
            page.go_back()
            page.locator(".ri-more-2-line").click()
            page.click("text=Delete project")
            self.assertEqual("Delete project XYZ?", page.text_content(".card h6"))
            # cancel
            page.click("text=Don't delete")
            self.assertEqual(
                page.url, f"{self.live_server_url}{reverse('users:profile')}"
            )
            page.go_back()
            # delete
            page.click("text=Yes, delete")
            self.assertEqual(
                page.url, f"{self.live_server_url}{reverse('users:profile')}"
            )
            self.assertEqual(
                "Project XYZ deleted.", page.text_content(".alert").strip()
            )
            # check mark deletion
            proj = models.Project.objects.get(pk=self.project.pk)
            self.assertIsNotNone(proj.deleted_at)
