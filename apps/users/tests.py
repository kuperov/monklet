from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.users.models import Profile
from django.urls import reverse_lazy
User = get_user_model()


email, pw = 'a@b.com', 'super secret'


class CreateProfileTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username=email, email=email, password=pw, first_name='Cornelius', last_name='Klonk')
        self.user.save()
        self.client.login(email=email, password=pw)

    def test_create_profile(self):
        self.assertIsNone(Profile.objects.filter(user_id = self.user.id).first())
        resp = self.client.get('/profile/', follow=True)
        self.assertIsNotNone(Profile.objects.get(user_id = self.user.id))
        self.assertContains(resp, 'Cornelius Klonk')


class UnauthenticatedProfileTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username=email, email=email, password=pw, first_name='Cornelius', last_name='Klonk')
        self.user.save()
        self.profile = Profile.objects.create(user=self.user)

    def test_unauthed_requests(self):
        for url in ['/profile/']:
            resp = self.client.get(url, follow=False)
            self.assertEqual(resp.status_code, 302)

    def test_update_other_profile(self):
        em2, pw2 = 'reg@hotmail.com', 'lemon tea'
        User.objects.create_user(username=em2, email=em2, password=pw2, first_name='Reginald', last_name='Goose')
        self.client.login(email=em2, password=pw2)
        edit_url = reverse_lazy('users:profile-edit', kwargs={'pk': self.user.id})  # self.user's profile page
        # regular user can't see others' update page
        self.assertContains(self.client.get(edit_url), 'not authorized', status_code=403)
        payload = {'institution': 'X', 'location': 'Y'}
        self.assertContains(self.client.post(edit_url, payload), 'not authorized', status_code=403)

    def test_admin_update(self):
        em2, pw2 = 'reg@hotmail.com', 'lemon tea'
        User.objects.create_user(
            username=em2, email=em2, password=pw2, first_name='Reginald', last_name='Goose', is_superuser=True)
        edit_url = reverse_lazy('users:profile-edit', kwargs={'pk': self.user.id})  # self.user's profile page
        self.client.login(email=em2, password=pw2)
        self.assertContains(self.client.get(edit_url), 'Institution', status_code=200)
        payload = {'institution': 'Blacktown Uni', 'location': 'Blacktown'}
        resp = self.client.post(edit_url, payload, follow=True)
        self.assertContains(resp, 'Reginald Goose', status_code=200)
        profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(profile.institution, 'Blacktown Uni')


class UpdateProfileTestCase(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username=email, email=email, password=pw, first_name='Cornelius', last_name='Klonk')
        self.user.save()
        self.profile = Profile.objects.create(user=self.user)
        self.client.login(email=email, password=pw)

    def test_update_own(self):
        edit_url = reverse_lazy('users:profile-edit', kwargs={'pk': self.user.id})  # self.user's profile page
        payload = {'institution': 'Blacktown Uni', 'location': 'Blacktown'}
        resp = self.client.post(edit_url, payload, follow=True)
        profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(profile.institution, 'Blacktown Uni')
        self.assertContains(resp, 'Cornelius Klonk', status_code=200)
