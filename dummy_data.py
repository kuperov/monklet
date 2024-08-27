import os
import django

user_data = [
    {'email': 'bob@bob.com', 'password': 'secret', 'first_name': 'Bob', 'last_name': 'Smith'},
    {'email': 'scott@dummy.com', 'password': 'tiger', 'first_name': 'Scott', 'last_name': 'Winston'},
    {'email': 'elly@hotmail.com', 'password': 'gimme', 'first_name': 'Elly', 'last_name': 'Turner'},
]
for i in range(len(user_data)):
    user_data[i]['username'] = user_data[i]['email']

projects = [
    {'name': 'Project 1', 'owner': 0, 'members': [1,3]},
    {'name': 'Project 2', 'owner': 1, 'members': [0,3]},
    {'name': 'Project 3', 'owner': 0, 'members': []},
    {'name': 'Project 4', 'owner': 1, 'members': []},
    {'name': 'Project 5', 'owner': 0, 'members': [1]}
]

members = set()
for p in projects:
    members.add(p['owner'])
    for m in p['members']:
        members.add(m)
max_index = len(members)

def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        django.setup()
        from apps.projects.models import Project, Membership
        from django.contrib.auth.models import User
        if User.objects.count() <= max_index + 1:
            for i in range(1 + max_index - User.objects.count()):
                u = User(**user_data[i])
                u.save()

        users = list(User.objects.all())

        for spec in projects:
            owner = users[spec['owner']]
            proj = Project(owner=owner, name=spec['name'], description='Lorem ipsum dolor sit amet')
            proj.save()
            for m in spec['members']:
                mship = Membership(project=proj, user=users[m])
                mship.save()
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__=='__main__':
    main()
