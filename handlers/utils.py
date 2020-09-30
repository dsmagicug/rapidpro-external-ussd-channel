from .models import Handler
from contacts.models import Contact
from channel.models import USSDSession
from channel.serializers import SessionSerializer
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from time import sleep
from ast import literal_eval
import re

RESPONSE_FORMAT = [
    (1, "Is Key Value"),
    (2, "Starts with")
]

METHODS = [
    ('POST', 'HTTP POST'),
    ('GET', 'HTTP GET'),
    ('PUT', 'HTTP PUT')
]

RESPONSE_CONTENT_TYPES = [
    ('json', 'application/json'),
    ('text', 'text/plain'),
    ('xml', 'application/xml')
]

SESSION_STATUSES = dict(
    TIMEDOUT='Timed Out',
    TERMINATED='Terminated',
    COMPLETED ='Completed'
)


def get_sessions():
    sessions = USSDSession.objects.all().order_by("-started_at")
    serializer = SessionSerializer(sessions, many=True)
    json_sessions = json.dumps(serializer.data)
    group_name = 'sessions'
    channel_layer = get_channel_layer()
    # broadcast sessions to group for live display
    sleep(0.02)  # be kind to the
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'report_sessions',
            'sessions': json_sessions
        }
    )


class ProcessAggregatorRequest:
    rapidpro_keys = []
    handler_keys = []
    standard_request = ''
    service_code = ''
    handler = None

    def __init__(self, aggregator_request):
        self.request_data = aggregator_request

    def separate_keys(self, string):
        """'
        @string => a string in the format of "{{short_code=ussdServiceCode}},  {{session_id=transactionId}}"
        """
        matches = re.compile('{{(.*?)}}', re.DOTALL).findall(string)
        for match in matches:
            split_list = match.split("=")
            self.rapidpro_keys.append(split_list[0].strip())
            self.handler_keys.append(split_list[1].strip())

        return [self.rapidpro_keys, self.handler_keys]

    def generate_standard_request(self):
        not_in_template = []  # all keys not defined in the template but exist in the request
        map_list = [
            (self.rapidpro_keys[self.handler_keys.index(key)], key) if key in self.handler_keys else (
                not_in_template.append(key)) for
            key in self.request_data.keys()]

        # remove all we never defined in the template
        [self.request_data.pop(v, None) for v in not_in_template if len(not_in_template) > 0]

        for item in map_list:
            if item is not None:
                # update request_data with new key names
                self.request_data[item[0]] = self.request_data.pop(item[1])
        if "session_id" not in self.request_data:
            raise Exception(
                f"Make sure your {{session_id=someThing}} is defined in aggregator {self.handler.aggregator}'s "
                f"Request Format settings")
        else:
            self.standard_request = self.request_data

    def process_handler(self):
        # determine service_code
        self.determine_service_code()
        self.handler = Handler.objects.get(short_code=self.service_code)
        request_format = self.handler.request_format
        # use defined template
        self.separate_keys(request_format)
        # generate standard request_string to send to rapidPro
        self.generate_standard_request()
        # save contact if it doesn't exist
        self.store_contact()
        return self.standard_request

    def determine_service_code(self):
        short_codes = Handler.objects.values_list('short_code', flat=True)
        codes = list(short_codes)
        for code in codes:
            if str(code) in self.request_data.values():
                self.service_code = str(code)

    def store_contact(self):
        if Contact.objects.filter(urn=self.standard_request['from']).exists():
            pass
        else:
            # created record
            Contact.objects.create(urn=self.standard_request['from'])

    def log_session(self):
        session_id = self.standard_request['session_id']
        contact = Contact.objects.get(urn=self.standard_request['from'])
        # check if session id exists with
        if USSDSession.objects.filter(session_id=session_id).exists():
            # do nothing to this session
            session = USSDSession.objects.get(session_id=session_id)
        else:
            # First End all sessions attached to this urn that may already be recorded
            USSDSession.objects.filter(contact=contact, status="In Progress").update(status='Terminated',
                                                                                     badge='warning',
                                                                                     ended_at=timezone.now())
            # create session
            session = USSDSession.objects.create(session_id=session_id, contact=contact, handler=self.handler)
            get_sessions()
        return session.session_id
