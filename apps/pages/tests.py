from django.test import TestCase
from django.urls import reverse_lazy
from apps.pages.models import Enquiry

import logging

class ErrorPageTestCase(TestCase):

    def setUp(self):
        self.logger = logging.getLogger()
        self.previous_level = self.logger.getEffectiveLevel()
        self.logger.setLevel(level=logging.CRITICAL)

    def tearDown(self):
        self.logger.setLevel(self.previous_level)

    def test_errors(self):
        resp = self.client.get("/urldoesntexist")
        self.assertContains(resp, "Not Found", status_code=404)
        resp = self.client.get("/404", follow=True)
        self.assertContains(resp, "Not Found", status_code=404)
        resp = self.client.get("/401", follow=True)
        self.assertContains(resp, "Unauthorized", status_code=401)
        resp = self.client.get("/403", follow=True)
        self.assertContains(resp, "Forbidden", status_code=403)
        resp = self.client.get("/400", follow=True)
        self.assertContains(resp, "Bad Request", status_code=400)
        resp = self.client.get("/500", follow=True)
        self.assertContains(resp, "Internal Server Error", status_code=500)


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
