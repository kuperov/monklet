from django.test import TestCase
from django.urls import reverse_lazy
from django.core import mail

from apps.projects import models
from apps.users.models import User

_e, _pw = "a@b.com", "tiger"


class InterviewTest(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(email=_e, password=_pw, name='Max Dingus')
        self.project = models.Project.objects.create(owner=self.owner, name="XYZ")
        self.bot_nc = models.Bot.objects.create(project=self.project, name='BBB', status='live', allow_public=True)
        self.letter = models.ConsentLetter.objects.create(
            project=self.project,
            name=".",
            short_md="# ABC\n\nabcdefg",
            letter_md="# PQR\n\npqrstuv **wx** yz",
        )
        self.bot_let = models.Bot.objects.create(
            project=self.project, name='C', allow_public=True, consent_letter=self.letter
        )

    def test_anonymous_no_letter(self):
        landing_page = reverse_lazy("bot-public", kwargs={"pk": self.bot_nc.pk})
        resp = self.client.get(landing_page)
        self.assertContains(resp, "XYZ")
        self.assertContains(resp, "I consent to participating")
        self.assertNotContains(resp, "full consent letter")
        # no consent
        resp = self.client.post(
            landing_page,
            {'subject_name': 'Bob',
             'subject_email': '',
             'proceed': 'Proceed'},
            follow=False)
        self.assertEqual(resp.status_code, 200)  # error
        self.assertContains(resp, 'This field is required.')
        # no name
        resp = self.client.post(
            landing_page,
            {'subject_name': '',
             'subject_email': '',
             'has_consented': 'on',
             'proceed': 'Proceed'},
            follow=False)
        self.assertEqual(resp.status_code, 200)  # error
        self.assertContains(resp, 'This field is required.')
        # followup but no email
        resp = self.client.post(
            landing_page,
            {'subject_name': 'Bob',
             'subject_email': '',
             'has_consented': 'on',
             'followup_consented': 'on',
             'proceed': 'Proceed'},
            follow=False)
        self.assertEqual(resp.status_code, 200)  # error
        self.assertContains(resp, 'Please provide your email address for follow-up.')
        resp = self.client.post(
            landing_page,
            {'subject_name': 'Bob',
             'subject_email': '',
             'has_consented': 'on',
             'proceed': 'Proceed'},
            follow=False)
        self.assertEqual(resp.status_code, 302)  # redirect
        iv = models.Interview.objects.get(pk=resp.url[-36:])
        self.assertEqual(iv.subject_name, 'Bob')
        self.assertEqual(iv.subject_email, '')
        resp = self.client.get(resp.url)
        self.assertContains(resp, self.bot_nc.name)  # smoke test

    def test_anonymous_with_letter(self):
        landing_page = reverse_lazy("bot-public", kwargs={"pk": self.bot_let.pk})
        resp = self.client.get(landing_page)
        self.assertContains(resp, "<h1>ABC</h1>")
        self.assertContains(resp, "<p>abcdefg</p>")
        let_url = reverse_lazy('consent-letter-public', kwargs={'pk': self.letter.pk})
        self.assertContains(resp, "full consent letter")
        self.assertContains(resp, let_url)
        resp = self.client.get(let_url)
        for t in ['<h1>PQR</h1>', '<p>pqrstuv <strong>wx</strong> yz']:
            self.assertContains(resp, t)

    def test_invite(self):
        self.assertTrue(self.client.login(email=_e, password=_pw))
        resp = self.client.get(self.project.bots_url)
        self.assertContains(resp, 'BBB', status_code=200)
        public_page = reverse_lazy("bot-public", kwargs={"pk": self.bot_let.pk})
        self.assertContains(resp, public_page, status_code=200)  # as menu item link
        project_inv = reverse_lazy('project-interviews-invite', kwargs={'pk': self.project.pk})
        bot_invite = f"{project_inv}?bot={self.bot_nc.pk}"
        self.assertContains(resp, bot_invite, status_code=200)  # will fail
        resp = self.client.get(bot_invite)
        # correct bot should be selected
        self.assertContains(resp, f'<option value="{self.bot_nc.pk}" selected>', status_code=200)
        # create invitation
        mail.outbox.clear()
        resp = self.client.post(project_inv, {'bot': self.bot_nc.pk, 'subject_name': 'Sally', 'subject_email': 'saz@hotmail.com', 'Save': 'save'})
        iv = models.Interview.objects.get(subject_email='saz@hotmail.com')
        iv_url = reverse_lazy('interview-landing', kwargs={'pk': iv.pk})
        self.assertEqual(iv.bot.pk, self.bot_nc.pk)
        self.assertEqual(iv.subject_name, 'Sally')
        msg = mail.outbox.pop()
        self.assertEqual(msg.to, ["Sally <saz@hotmail.com>"])
        self.assertIn(str(iv_url), msg.body)
