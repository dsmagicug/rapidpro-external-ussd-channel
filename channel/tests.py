from django.test import TestCase, Client
from .views import ChannelConf
from .models import USSDChannel, USSDSession
from contacts.models import Contact
from handlers.models import Handler
from django.urls import reverse, resolve
from countries_plus.models import Country
from .forms import ChannelConfForm


class TestChannelUrls(TestCase):
    def test_handler_list_url(self):
        url = reverse("channel_conf")
        resolver = resolve(url)
        self.assertEqual(resolver.func.__name__, ChannelConf.as_view().__name__)


class TestChannelViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.config_channel_url = reverse('channel_conf')
        self.config_channel_template = 'channel/conf.html'
        self.country = Country.objects.create(
            iso="UG",
            iso3="UGA",
            iso_numeric=256,
            name="UGANDA",
            capital="KAMPALA",
            population=40000000,
            continent="AF"
        )
        self.channel = USSDChannel.objects.create(
            send_url="DMARK",
            rapidpro_receive_url="*256#",
            timeout_after=10,
            trigger_word="USSD",
            country=self.country
        )

    def test_channel_config_GET(self):
        response = self.client.get(self.config_channel_url)
        self.assertEquals(response.status_code, 302)

    def test_channel_config_POST(self):
        response = self.client.post(self.config_channel_url, {})
        self.assertEquals(response.status_code, 302)  # check for a redirect


# test Form
class TestChannelForm(TestCase):

    def setUp(self):
        self.country = Country.objects.create(
            iso="UG",
            iso3="UGA",
            iso_numeric=256,
            name="UGANDA",
            capital="KAMPALA",
            population=40000000,
            continent="AF"
        )

    def testChannelForm(self):
        form = ChannelConfForm(
            data={
                "send_url": "https://ussd-channel.app.com",
                "rapidpro_receive_url": "https://rapidpro.app.com/c/ex/channel_uuid/receive",
                "timeout_after": 10,
                "trigger_word": "USSD",
                "country": self.country
            }
        )
        self.assertTrue(form.is_valid())

    def testChannelFormInvalid(self):
        form = ChannelConfForm(
            data=dict()
        )
        self.assertFalse(form.is_valid())


class TestChannelModel(TestCase):

    def setUp(self):
        self.country = Country.objects.create(
            iso="UG",
            iso3="UGA",
            iso_numeric=256,
            name="UGANDA",
            capital="KAMPALA",
            population=40000000,
            continent="AF"
        )
        self.channel = USSDChannel.objects.create(
            send_url="https://ussd-channel.app.com",
            rapidpro_receive_url="https://rapidpro.app.com/c/ex/channel_uuid/receive",
            timeout_after=10,
            trigger_word="USSD",
            country=self.country
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
        # This tests the Contact Model
        self.contact = Contact.objects.create(
            urn="256787411849"
        )

    def test_channel_creation(self):
        self.assertEquals(USSDChannel.objects.count(), 1)

    def test_ussd_session_creation(self):
        USSDSession.objects.create(
            session_id="123456789",
            contact=self.contact,
            handler=self.handler,
        )
        self.assertEquals(USSDSession.objects.count(), 1)
