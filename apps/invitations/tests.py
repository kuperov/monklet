
from django.core import mail
from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()
from apps.projects.models import Project, Member
from django.urls import reverse_lazy
from django.utils.timezone import now
from datetime import timedelta
from django.conf import settings

from apps.invitations.models import MemberInvitation

o_e, o_pw, o_n = 'a@b.com', 'super secret', ['John', 'Green'] # owner
r_e, r_pw = 'r@s.com', 'very secret'  # recipient


class ReqMock:
    def build_absolute_uri(self, uri):
        return settings.BASE_URL+uri


class InvitationModelTestCase(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username=o_e, email=o_e, password=o_pw
        )
        self.project = Project.objects.create(
            owner=self.owner, name='Foo'
        )

    def test_expiry(self):
        default = MemberInvitation.objects.create(project=self.project, email=r_e, role='editor')
        self.assertEqual(default.status, 'Not sent')
        self.assertFalse(default.is_valid)
        default.send_email(ReqMock())
        self.assertEqual(default.status, 'Valid')
        self.assertTrue(default.is_valid)
        self.assertFalse(default.is_expired)
        self.assertAlmostEqual((default.expires_at - now()) / timedelta(days=1), 7.0, places=1)
        default.expire()
        self.assertEqual(default.status, 'Expired')
        self.assertTrue(default.is_expired)

class InvitationTestCase(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username=o_e, email=o_e, password=o_pw
        )
        self.project = Project.objects.create(
            owner=self.owner, name='Foo'
        )
        self.invitation = MemberInvitation.objects.create(
            project=self.project,
            email='dest@example.com',
            name='Rob Recipient',
            message='Come and collaborate on Foo',
            subject='Collaborate on Foo',
            role='editor',
            sent_at=now()
        )

    def test_owner_clicks(self):
        self.client.login(email=o_e, password=o_pw)
        resp = self.client.get(self.invitation.landing_url, follow=False)
        self.assertContains(resp, 'not permitted', status_code=403)
        accept_action = reverse_lazy('invitation-respond', kwargs={'code': self.invitation.pk})
        resp = self.client.post(accept_action, data={'yes': 'Yes, accept'}, follow=False)
        self.assertContains(resp, 'not permitted', status_code=403)

    def test_accept_invitation(self):
        self.assertEqual(self.project.member_count, 1)
        self.assertFalse(self.invitation.is_expired)
        self.assertTrue(self.invitation.is_valid)
        # not logged in
        resp = self.client.get(self.invitation.landing_url, follow=True)
        self.assertContains(resp, 'Sign up', status_code=200)
        self.assertNotContains(resp, 'Yes')
        # logged in
        recip = User.objects.create_user(username=r_e, email=r_e, password=r_pw)
        self.client.login(email=r_e, password=r_pw)
        resp = self.client.get(self.invitation.landing_url, follow=True)
        self.assertNotContains(resp, 'Sign up')
        self.assertContains(resp, 'Yes, accept', status_code=200)
        accept_action = reverse_lazy('invitation-respond', kwargs={'code': self.invitation.pk})
        resp = self.client.post(accept_action, {'yes': 'Yes, accept'}, follow=False)
        self.assertRedirects(resp, self.project.url)
        proj = Project.objects.get(pk=self.project.pk)
        self.assertEqual(proj.member_count, 2)
        self.assertTrue(self.project.is_member(recip))
        mem = Member.objects.get(project=self.project, user=recip)
        self.assertEqual(mem.role, 'editor')
        inv = MemberInvitation.objects.get(pk=self.invitation.pk)
        self.assertTrue(inv.is_expired)
        self.assertFalse(inv.is_valid)

    def test_email_sending(self):
        mail.outbox.clear()
        req_mock = ReqMock()
        self.invitation.send_email(req_mock)
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual('Collaborate on Foo', msg.subject)
        self.assertTrue(f'{settings.BASE_URL}{self.invitation.landing_url}' in msg.body)
