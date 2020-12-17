from django.test import TestCase, Client
from django.urls import reverse, resolve
from .views import index, graph_data


class TestUiUrls(TestCase):
    def test_dasboard_url(self):
        url = reverse("home")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, index.__name__)

    def test_graph_endpoint(self):
        url = reverse("graph")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, graph_data.__name__)


class TestUiViews(TestCase):

    def setUp(self):
        self.template = "index.html"
        self.client = Client()

    def test_ui_dashboard_view_GET(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 302)


