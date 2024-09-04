
from django.test import TestCase
from apps.projects.models import Project, Member
from django.contrib.auth import get_user_model
User = get_user_model()

# https://channels.readthedocs.io/en/stable/tutorial/part_4.html

o_e, o_pw, o_n = 'a@b.com', 'super secret', ['John', 'Green'] # owner
v_e, v_pw, v_n = 'b@b.com', 'secret', ['Bob', 'Black']  # viewer
e_e, e_pw, e_n = 'c@b.com', 'secret', ['Alex', 'White']  # editor
n_e, n_pw = 'e@b.com', 'secret'  # no access

creds = {o_e: o_pw, v_e: v_pw, e_e: e_pw, n_e: n_pw}

class AccessTestCase(TestCase):

    def setUp(self):
        self.owner = User.objects.create_user(
            username=o_e, email=o_e, password=o_pw
        )
        self.viewer = User.objects.create_user(
            username=v_e, email=v_e, password=v_pw
        )
        self.editor = User.objects.create_user(
            username=e_e, email=e_e, password=e_pw
        )
        self.noaccess = User.objects.create_user(
            username=n_e, email=n_e, password=n_pw
        )
        self.project = Project.objects.create(
            owner=self.owner, name='Foo'
        )
        for u, r in [
                (self.viewer, 'viewer'),
                (self.editor, 'editor'),
            ]:
            Member.objects.create(project=self.project, user=u, role=r)

    def test_access(self):
        self.assertTrue(self.project.can_edit(self.editor))
        self.assertFalse(self.project.can_edit(self.viewer))
        self.assertTrue(self.project.can_view(self.editor))
        self.assertTrue(self.project.can_view(self.viewer))
        self.assertFalse(self.project.can_edit(self.noaccess))
        self.assertFalse(self.project.can_view(self.noaccess))
        self.assertTrue(self.project.is_member(self.owner))
        self.assertTrue(self.project.is_member(self.editor))
        self.assertTrue(self.project.is_member(self.viewer))
        self.assertFalse(self.project.is_member(self.noaccess))
        self.assertFalse(self.project.is_member(None))

    def test_properties(self):
        self.assertEqual(self.project.member_count, 3)  # owner, editor, viewer

    def check_get_access(self, props, email_access):
        urls = [getattr(self.project, f) for f in props]
        for email, can_access in email_access.items():
            self.client.login(email=email, password=creds[email])
            for url in urls:
                resp = self.client.get(url, follow=True)
                if can_access:
                    if 'not authorized' in resp.content.decode('utf-8'):
                        breakpoint()
                    self.assertNotContains(resp, 'not authorized')
                else:
                    self.assertContains(resp, 'not authorized')
            self.client.logout()

    def test_auth(self):
        fns = ['analysis_url', 'bots_url', 'files_url', 'invitations_url',
               'questions_url', 'members_url', 'responses_url', 'url']
        self.check_get_access(fns, {o_e: True, v_e: True, e_e: True, n_e: False})
        self.check_get_access(['settings_url'], {o_e: True, v_e: False, e_e: False, n_e: False})
        self.check_get_access(['delete_url'], {o_e: True, v_e: False, e_e: False, n_e: False})
        self.check_get_access(['leave_url'], {o_e: False, v_e: True, e_e: True, n_e: False})
