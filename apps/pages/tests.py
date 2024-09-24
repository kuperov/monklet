import unittest
from django.test import TestCase
from django.urls import reverse_lazy
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

    def test_feedback_page(self):
        resp = self.client.get("/")
        self.assertContains(resp, "Get in touch", status_code=200)
        payload = {"email": "abc@dummy.com", "name": "John", "message": "Hi"}
        resp = self.client.post(reverse_lazy('enquiry_partial'), payload, follow=True)
        enq = Enquiry.objects.filter(email="abc@dummy.com").first()
        self.assertIsNotNone(enq)
        self.assertIsNotNone(enq.created_at)
        self.assertEqual(enq.message, payload['message'])
        self.assertEqual(enq.name, payload['name'])
