from django.test import TestCase
from apps.projects import models
from apps.users.models import User


def _init_project_login(testcase):
    em, pw = 'a@b.com', 'secret'
    testcase.owner = User.objects.create_user(email=em, password=pw, name="Max Dingus")
    testcase.project = models.Project.objects.create(owner=testcase.owner, name="XYZ")
    testcase.bot = models.Bot.objects.create(
        project=testcase.project, name="BBB", status="live", allow_public=True
    )
    testcase.client.login(em, pw)

class TestImport(TestCase):

    def setUp(self):
        _init_project_login(self)
