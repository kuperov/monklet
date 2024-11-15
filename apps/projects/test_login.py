from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from playwright import sync_playwright

from apps.users.models import User


class MyViewTests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.owner = User.objects.create_user(email='a@b.com', password='secret')

    def test_login(self):
        page = self.browser.newPage()
        page.goto('%s%s' % (self.live_server_url, '/login/'))
        page.fill('#username', 'a@b.com')
        page.fill('#password', 'secret')
        page.click('text=Log in')
        assert page.url == '%s%s' % (self.live_server_url, '/profile/')
        page.close()
