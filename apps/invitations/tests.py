from django.test import TestCase
from django.contrib.auth.models import User
from apps.projects.models import Project, Membership
from django.urls import reverse_lazy

o_e, o_pw = 'a@b.com', 'super secret' # owner
r_e, r_pw = 'r@s.com', 'very secret'  # recipient

class InvitationTestCase(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username=o_e, email=o_e, password=o_pw
        )
        self.project = Project.objects.create(
            owner=self.owner, name='Foo'
        )
        self.invitation = Membership.objects.create(
            project=self.project,
            invitation_email='dest@example.com',
            invitation_name='Rob Recipient',
            invitation_message='Collaborate on Foo',
            status='invited',
            role='editor'
        )

    def test_owner_clicks(self):
        self.client.login(email=o_e, password=o_pw)
        resp = self.client.get(self.invitation.invitation_landing_url, follow=True)
        self.assertContains(resp, 'not permitted', status_code=403)
        accept_action = reverse_lazy('invitation-respond', kwargs={'code': self.invitation.invitation_code})
        resp = self.client.post(accept_action, data={'yes': 'Yes, accept'}, follow=False)
        self.assertContains(resp, 'not permitted', status_code=403)


    def test_accept_invitation(self):
        self.assertEqual(self.project.member_count, 1)
        # not logged in
        resp = self.client.get(self.invitation.invitation_landing_url, follow=True)
        self.assertContains(resp, 'Sign up', status_code=200)
        self.assertNotContains(resp, 'Yes')
        # logged in
        User.objects.create_user(username=r_e, email=r_e, password=r_pw)
        self.client.login(email=r_e, password=r_pw)
        resp = self.client.get(self.invitation.invitation_landing_url, follow=True)
        self.assertNotContains(resp, 'Sign up')
        self.assertContains(resp, 'Yes, accept', status_code=200)
        accept_action = reverse_lazy('invitation-respond', kwargs={'code': self.invitation.invitation_code})
        resp = self.client.post(accept_action, {'yes': 'Yes, accept'}, follow=False)
        self.assertRedirects(resp, self.project.url())
        proj = Project.objects.get(pk=self.project.pk)
        self.assertEqual(proj.member_count, 2)
        mship = Membership.objects.get(pk=self.invitation.pk)
        self.assertEqual(mship.status, 'accepted')

    def test_decline_invitation(self):
        self.assertEqual(self.project.member_count, 1)
        User.objects.create_user(username=r_e, email=r_e, password=r_pw)
        self.client.login(email=r_e, password=r_pw)
        accept_action = reverse_lazy('invitation-respond', kwargs={'code': self.invitation.invitation_code})
        resp = self.client.post(accept_action, data={'no': 'No, decline'}, follow=False)
        self.assertRedirects(resp, reverse_lazy('profile'))
        proj = Project.objects.get(pk=self.project.pk)
        self.assertEqual(proj.member_count, 1)
        mship = Membership.objects.get(pk=self.invitation.pk)
        self.assertEqual(mship.status, 'declined')
