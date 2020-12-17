from django.test import SimpleTestCase, TestCase, Client
from django.urls import reverse, resolve

from .views import HandlersListView, RegisterHandlerView
from .models import Handler
from .forms import HandlerForm
from .utils import separate_keys, ProcessAggregatorRequest
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
        response = self.client.post(self.add_handler_url, {})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, self.add_handler_template)


# test Form
class TestHandlerForm(TestCase):
    def testHandlerForm(self):
        form = HandlerForm(
            data={
                "aggregator": "DMARK",
                "short_code": "*256#",
                "request_format": "{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                                  "{{text=ussdRequestString}}",
                "response_content_type": "json",
                "response_method": "POST",
                "response_format": 1,
                "signal_reply_string": "request",
                "response_structure": "{{text=responseString}}, {{action=action}}",
                "signal_end_string": "end",
                "push_support": True,
                "push_url": "http://unicef.app"
            }
        )
        self.assertTrue(form.is_valid())

    def testHandlerFormInvalid(self):
        # form data missing short_code and aggregator name
        form = HandlerForm(
            data={
                "request_format": "{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                                  "{{text=ussdRequestString}}",
                "response_content_type": "json",
                "response_method": "POST",
                "response_format": 1,
                "signal_reply_string": "request",
                "response_structure": "{{text=responseString}}, {{action=action}}",
                "signal_end_string": "end",
                "push_support": True,
                "push_url": "http://unicef.app"
            }
        )
        self.assertFalse(form.is_valid())


class TestHandlerModel(TestCase):

    def setUp(self):
        self.handler = Handler.objects.create(
            aggregator="DMARK",
            short_code="*256#",
            request_format="{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                           "{{text=ussdRequestString}}",
            response_content_type="json",
            response_method="POST",
            response_format=1,
            signal_reply_string="request",
            response_structure="{{text=responseString}}, {{action=action}}",
            signal_end_string="end",
            push_support=True,
            push_url="http://unicef.app"
        )

    def test_handler_creation(self):
        self.assertEquals(self.handler.aggregator, "DMARK")


class TestHandlerUtils(TestCase):
    def setUp(self):
        self.cgi_string = "{{short_code=ussdServiceCode}}, {{session_id=transactionId}}"
        self.request_data = dict(
            ussdRequestString="",
            msisdn="256787411849",
            ussdServiceCode="255",
            transactionId=13264738487
        )
        self.handler = Handler.objects.create(
            aggregator="DMARK",
            short_code="255",
            request_format="{{short_code=ussdServiceCode}},  {{session_id=transactionId}}, {{from=msisdn}}, "
                           "{{text=ussdRequestString}}",

            response_structure="{{text=responseString}}, {{action=action}}",
            signal_reply_string="request",
            signal_end_string="end",
            push_support=False,
            push_url=""
        )
        self.sr = ProcessAggregatorRequest(self.request_data)

    def test_ProcessAggregatorRequest(self):
        # test object creation with type class
        self.assertIsInstance(self.sr, ProcessAggregatorRequest)

    def test_separate_keys(self):
        # returns a list of lists with exactly 2 lists
        result = separate_keys(self.cgi_string)
        self.assertTrue(isinstance(result, list))
        self.assertTrue(len(result), 2)
        self.assertTrue(isinstance(result[0], list))
        self.assertTrue(isinstance(result[1], list))

    def test_process_handler(self):
        standard_request = self.sr.process_handler()
        self.assertIsInstance(standard_request, dict)


