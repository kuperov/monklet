import os
import django


user_data = [
    {'email': 'alice.johnson@email.com', 'password': 'welcome123', 'name': 'Alice Johnson'},
    {'email': 'ben.miller@example.com', 'password': 'testingapp', 'name': 'Ben Miller'},
    {'email': 'clara.lee@workmail.com', 'password': 'password1!', 'name': 'Clara Lee'},
    {'email': 'david.hernandez@yahoo.com', 'password': 'ilovemypet', 'name': 'David Hernandez'},
    {'email': 'emily.chen@gmail.com', 'password': 'strongpass', 'name': 'Emily Chen'},
    {'email': 'frank.nguyen@hotmail.com', 'password': 'testing1234', 'name': 'Frank Nguyen'},
    {'email': 'grace.walker@outlook.com', 'password': 'apptest123', 'name': 'Grace Walker'},
    {'email': 'henry.davis@email.com', 'password': 'securepass', 'name': 'Henry Davis'},
    {'email': 'isla.garcia@workmail.com', 'password': 'mysecureapp', 'name': 'Isla Garcia'},
    {'email': 'kimberly.young@gmail.com', 'password': 'supersecure', 'name': 'Kimberly Young'},
    {'email': 'liam.lewis@hotmail.com', 'password': 'verystrong', 'name': 'Liam Lewis'},
    {'email': 'mia.williams@outlook.com', 'password': 'ilovedogs', 'name': 'Mia Williams'},
    {'email': 'noah.brown@email.com', 'password': 'secureapp123', 'name': 'Noah Brown'},
]
non_user_data = [
    {'email': 'olivia.jones@workmail.com', 'name': 'Olivia Jones'},
    {'email': 'william.miller@yahoo.com', 'name': 'William Miller'},
    {'email': 'sophia.davis@gmail.com', 'name': 'Sophia Davis'},
    {'email': 'ethan.garcia@hotmail.com', 'name': 'Ethan Garcia'},
    {'email': 'isabella.martin@outlook.com', 'name': 'Isabella Martin'},
]
for i in range(len(user_data)):
    user_data[i]['username'] = user_data[i]['email']

projects = [
    {'name': 'Attitudes toward AI', 'owner': 0, 'members': [1,3], 'invited': [0,1]},
    {'name': 'Living in Melbourne', 'owner': 1, 'members': [0,3], 'invited': []},
    {'name': 'Stress in first responders', 'owner': 0, 'members': [], 'invited': [0,1,2,3]},
    {'name': 'Pressure to perform at school', 'owner': 1, 'members': [], 'invited': [0,1,2,3]},
    {'name': 'Climate change and coastal communities', 'owner': 0, 'members': [1,2,3], 'invited': [4]},
    {'name': 'Technology in education', 'owner': 1, 'members': [0,3], 'invited': [3]},
    {'name': 'Meditation and stress reduction', 'owner': 2, 'members': [0,1,3], 'invited': [2]},
    {'name': 'Procrastination among bus drivers', 'owner': 3, 'members': [0,1,2], 'invited': [1,2]},
    {'name': 'Artificial intelligence researchers', 'owner': 0, 'members': [1,3], 'invited': [1]},
    {'name': 'Anxiety about work', 'owner': 1, 'members': [0,2], 'invited': [2]},
    {'name': 'Social media on mental health', 'owner': 2, 'members': [0,1,3], 'invited': [3]},
    {'name': 'Bilingualism and discrimination', 'owner': 3, 'members': [0,1,2], 'invited': [4]},
    {'name': 'Depression and color', 'owner': 0, 'members': [1,3], 'invited': [0]},
    {'name': 'Toddlers and space exploration', 'owner': 1, 'members': [0,2], 'invited': []},
    {'name': 'Video games and children', 'owner': 2, 'members': [0,1,3], 'invited': [3]},
    {'name': 'Physical activity and mental health', 'owner': 3, 'members': [0,1,2], 'invited': [3]},
    {'name': 'Marital status and persuasion', 'owner': 0, 'members': [1,3], 'invited': [1,2]},
    {'name': 'Artificial intelligence and real estate', 'owner': 1, 'members': [0,2], 'invited': []},
    {'name': 'Anxiety about automation', 'owner': 2, 'members': [0,1,3], 'invited': []}
]

members = set()
for p in projects:
    members.add(p['owner'])
    for m in p['members']:
        members.add(m)
max_index = len(members)

def main():
    os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
    try:
        django.setup()
        from apps.projects.models import Project, Member, MemberInvitation
        from apps.users.models import User

        if User.objects.count() <= max_index + 1:
            for i in range(1 + max_index - User.objects.count()):
                u = User(**user_data[i])
                u.save()

        users = list(User.objects.all())

        for spec in projects:
            owner = users[spec['owner']]
            proj = Project(owner=owner, name=spec['name'], description='Lorem ipsum dolor sit amet')
            proj.save()
            for i, m in enumerate(spec['members']):
                name = user_data[m]['name']
                mship = Member(
                    project=proj,
                    user=users[m],
                    role=['editor','viewer'][i % 2]
                )
                mship.save()
            for i, m in enumerate(spec['invited']):
                name = user_data[m]['name']
                mship = MemberInvitation(
                    project=proj,
                    email=non_user_data[m]['email'],
                    name=name,
                    message='Please work with us',
                    role=['editor','viewer'][i % 2]
                )
                mship.save()
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

if __name__=='__main__':
    main()
