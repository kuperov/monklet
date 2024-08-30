
from django.test import TestCase
from apps.projects.models import Project, Member
from django.contrib.auth.models import User

o_e, o_pw, o_n = 'a@b.com', 'super secret', ['John', 'Green'] # owner
v_e, v_pw, v_n = 'b@b.com', 'secret', ['Bob', 'Black']  # viewer
e_e, e_pw, e_n = 'c@b.com', 'secret', ['Alex', 'White']  # editor
i_e, i_pw = 'd@b.com', 'secret'  # invited
n_e, n_pw = 'e@b.com', 'secret'  # no access

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
        # generated
        self.assertEqual(self.project.analysis_url(), f"/projects/{self.project.pk}/analysis")
        self.assertEqual(self.project.bots_url(), f"/projects/{self.project.pk}/bots")
        self.assertEqual(self.project.data_url(), f"/projects/{self.project.pk}/data")
        self.assertEqual(self.project.delete_url(), f"/projects/{self.project.pk}/delete")
        self.assertEqual(self.project.files_url(), f"/projects/{self.project.pk}/files")
        self.assertEqual(self.project.invitations_url(), f"/projects/{self.project.pk}/invitations")
        self.assertEqual(self.project.leave_url(), f"/projects/{self.project.pk}/leave")
        self.assertEqual(self.project.members_url(), f"/projects/{self.project.pk}/members")
        self.assertEqual(self.project.questions_url(), f"/projects/{self.project.pk}/questions")
        self.assertEqual(self.project.responses_url(), f"/projects/{self.project.pk}/responses")
        self.assertEqual(self.project.settings_url(), f"/projects/{self.project.pk}/settings")
        self.assertEqual(self.project.url(), f"/projects/{self.project.pk}/")
