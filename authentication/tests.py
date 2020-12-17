from django.test import SimpleTestCase, TestCase
from django.urls import reverse, resolve
from .views import login_view, profile
from .forms import LoginForm


class TestAuthUrls(SimpleTestCase):
    def setUp(self):
        self.login_url = reverse("login")
        self.logout = reverse("logout")
        self.profile = reverse("profile")

    def test_auth_login_url(self):
        resolver = resolve(self.login_url)
        self.assertEqual(resolver.func.__name__, login_view.__name__)


# test handler Views
class TestLoginForm(TestCase):
    def test_login_form_valid(self):
        form = LoginForm(
            data={
                "username": "tester",
                "password": "tester12345",
            }
        )
        self.assertTrue(form.is_valid())

    def test_login_form_invalid(self):
        form = LoginForm(
            data={
                "userame": "tester",
                "email": "tester@wrong.com",
            }
        )
        self.assertFalse(form.is_valid())
