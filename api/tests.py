from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from rest_framework.test import APIRequestFactory, APIClient, RequestsClient, force_authenticate

from .views import send_url, call_back
from channel.models import USSDSession, USSDChannel
from handlers.models import Handler
from countries_plus.models import Country


class TestApiEndPoints(TestCase):

    def test_send_url_endpoint(self):
        url = reverse("send_url")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, send_url.__name__)

    def test_call_back_endpoint(self):
        url = reverse("callback")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, call_back.__name__)


class TestApiViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.send_url = reverse("send_url")
        self.callback_url = reverse("callback")
        self.factory = APIRequestFactory()
        self.client = RequestsClient()
        self.user = User.objects.create_user('tester', 'tester@testing.com', 'test12345')
        self.auth_client = APIClient()
        self.auth_client.force_authenticate(user=self.user)
        self.handler = Handler.objects.create(
            aggregator="DMARK2",
            short_code="258",
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
        self.country = Country.objects.create(
            iso="UG",
            iso3="UGA",
            iso_numeric=256,
            name="UGANDA",
            capital="KAMPALA",
            population=40000000,
            continent="AF",
            phone="256"
        )
        self.channel = USSDChannel.objects.create(
            send_url="DMARK",

            # Note you may replace this with an working url to run the commented out test
            rapidpro_receive_url="http://localhost/c/x/channel_uuid/receive",
            timeout_after=10,
            trigger_word="USSD",
            country=self.country
        )

    def test_send_url_view(self):
        request = self.factory.post(reverse("send_url"))
        self.assertTrue(request)
        response = self.client.post(
            f"https://localhost{self.send_url}",
            json={
                "to_no_plus": "256787411849",
                "session_status": "W",
                "text": "How old are you"
            },
            headers={'CONTENT_TYPE': "application/json"}
        )
        self.assertTrue(response.status_code, 200)

    # def test_call_back_view(self):
    #     response = self.auth_client.post(
    #         f"https://localhost{self.callback_url}",
    #         {
    #             "ussdRequestString": "USSD",
    #             "msisdn": "0755387533",
    #             "ussdServiceCode": "258",
    #             "transactionId": 16786830012
    #         },
    #         format="json",
    #         headers={'CONTENT_TYPE': "application/json"}
    #     )
    #     self.assertTrue(response.status_code, 200)
