from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve
from .views import HandlersListView, RegisterHandlerView
from .models import Handler
import json


# test handler List URL
class TestHandlerUrls(SimpleTestCase):

    def test_handler_list_url(self):
        url = reverse("handlers")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, HandlersListView.as_view().__name__)

    def test_handler_add_handler_url(self):
        url = reverse('add_handler')
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, RegisterHandlerView.as_view().__name__)

    def test_handler_edit_handler_url(self):
        url = reverse('edit_handler', kwargs={'handler_id': 4})
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, RegisterHandlerView.as_view().__name__)


# test handler Views
class TestHandlerViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.list_handlers = reverse('handlers')
        self.add_handler_url = reverse('add_handler')
        self.add_handler_template = 'handlers/add_handler.html'
        self.handler = Handler.objects.create(
            aggregator="DMARK",
            short_code="*256#",
            request_format="{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                           "{{text=ussdRequestString}}",

            response_structure="{{text=responseString}}, {{action=action}}",
            signal_reply_string="request",
            signal_end_string="end",
            push_support=False,
            push_url=""
        )

    def test_handler_list_GET(self):
        template_name = 'handlers/handler.html'

        response = self.client.get(self.list_handlers)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)

    def test_add_handler_GET(self):

        response = self.client.get(self.add_handler_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.add_handler_template)

    def test_add_handler_POST(self):

        response = self.client.post(self.add_handler_url, dict(
            aggregator="DMARK",
            short_code="*256#",
            request_format="{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                           "{{text=ussdRequestString}}",

            response_structure="{{text=responseString}}, {{action=action}}",
            signal_reply_string="request",
            signal_end_string="end",
            push_support=False,
            push_url=""
        ))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.add_handler_template)

    def test_add_handler_POST_no_data(self):
        response = self.client.post(self.add_handler_url)
        self.assertEquals(response.status_code, 200)
        print(response.context['success'])
        self.assertTemplateUsed(response, self.add_handler_template)
