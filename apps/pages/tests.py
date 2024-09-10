import unittest
from django.test import TestCase
from apps.pages.models import Enquiry


class ErrorPageTestCase(TestCase):

    @unittest.skip("Not returning correct status codes")
    def test_errors(self):
        resp = self.client.get("/urldoesntexist")
        self.assertContains(resp, "not found", status_code=404)
        resp = self.client.get("/404", follow=True)
        self.assertContains(resp, "not found", status_code=404)
        resp = self.client.get("/403", follow=True)
        self.assertContains(resp, "not authorized", status_code=403)
        resp = self.client.get("/400", follow=True)
        self.assertContains(resp, "bad request", status_code=400)
        resp = self.client.get("/500", follow=True)
        self.assertContains(resp, "server error", status_code=500)


class FrontPagesTestCase(TestCase):

    def test_placeholder_page(self):
        resp = self.client.get("/")
        self.assertContains(resp, "We're launching soon.", status_code=200)
        resp = self.client.post("/", {"email": "abc@dummy.com"}, follow=True)
        enq = Enquiry.objects.filter(email="abc@dummy.com").first()
        self.assertIsNotNone(enq)
        self.assertIsNotNone(enq.created_at)
        # IP address?
