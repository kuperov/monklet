# from config import settings
# settings.configure()

from apps.projects.models import Project
from django.contrib.auth.models import User

user = User.objects.first()
if not user.projects.filter(name='Project 1'):
    proj1 = Project(owner=user, name='Project 1', description='Lorem ipsum dolor sit amet')
    proj1.save()
if not user.projects.filter(name='Project 2'):
    proj2 = Project(owner=user, name='Project 2', description='Lorem ipsum dolor sit amet')
    proj2.save()
if not user.projects.filter(name='Project 3'):
    proj3 = Project(owner=user, name='Project 3', description='Lorem ipsum dolor sit amet')
    proj3.save()
if not user.projects.filter(name='Project 4'):
    proj4 = Project(owner=user, name='Project 4', description='Lorem ipsum dolor sit amet')
    proj4.save()
