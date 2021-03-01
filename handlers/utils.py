from .models import Handler
from contacts.models import Contact
from channel.models import USSDSession, USSDChannel
from channel.serializers import SessionSerializer
from django.utils import timezone
from django.conf import settings
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from countries_plus.models import Country
import json
from time import sleep, time
from core.utils import error_logger, access_logger
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
AUTH_SCHEMES = [
    ("TOKEN", "TOKEN"),
    ("NONE", "NONE"),
]

RESPONSE_CONTENT_TYPES = [
    ('json', 'application/json'),
    ('form-urlencoded', 'application/x-www-form-urlencoded'),
    ('text', 'text/plain'),
    ('xml', 'application/xml'),
]
RP_RESPONSE_CONTENT_TYPES = {
    "JSON": "application/json",
    "URL_ENCODED": "application/x-www-form-urlencoded",
    "TEXT": "text/plain",
    "XML": "application/xml"
}
SESSION_STATUSES = dict(
    TIMED_OUT='Timed Out',
    TERMINATED='Terminated',
    COMPLETED='Completed',
    IN_PROGRESS="In Progress"
)

RP_RESPONSE_FORMAT = {
    "text": "text",
    "to": "to",
    "session_status": "session_status"
}

RP_RESPONSE_STATUSES = {
    "waiting": "W"
}


def get_sessions():
    sessions = USSDSession.objects.all().order_by("-last_access_at")
    serializer = SessionSerializer(sessions, many=True)
    json_sessions = json.dumps(serializer.data)
    group_name = 'sessions'
    channel_layer = get_channel_layer()
    # broadcast sessions to group for live display
    sleep(0.02)  # being kind to the system
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'report_sessions',
            'sessions': json_sessions
        }
    )


# get configured channel, we can't simply assume the pk=1
def get_channel():
    channels = USSDChannel.objects.all()
    if len(channels) > 0:
        return channels[0]
    else:
        return None


def separate_keys(string):
    """'
    @string => a string in the format of "{{short_code=ussdServiceCode}},  {{session_id=transactionId}}"
    """
    rapidpro_keys = []
    aggregator_keys = []
    matches = re.compile('{{(.*?)}}', re.DOTALL).findall(string)
    for match in matches:
        split_list = match.split("=")
        rapidpro_keys.append(split_list[0].strip())
        aggregator_keys.append(split_list[1].strip())

    return [rapidpro_keys, aggregator_keys]


def standard_urn(urn):
    channel = get_channel()
    country = channel.country_id
    country_obj = Country.objects.get(iso=country)
    dial_code = country_obj.phone
    if urn[0] == "0":
        # add prefix
        urn = re.sub('0', dial_code, urn, 1)
    else:
        urn = urn
    return urn


def create_session(urn, session_status):
    ''''
    for test purposes
    a smarter one will be created once we have an aggregator that supports push
    '''
    session_id = str(time()).replace(".", "")


def clear_timedout_sessions():
    # lets create a 5 mins scheduler
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=5,  # five seconds
        period=IntervalSchedule.SECONDS,
    )

    # create the periodic task to run using the above scheduler
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name='Clear_Timedout_sessions',
        task='api.tasks.clear_timed_out_sessions',
    )
    # Periodic task to expire contacts out of their flows using handler's set expire_on_inactivity_of
    PeriodicTask.objects.get_or_create(  # get_or_create ensures task is created only once
        interval=schedule,
        name='Expire_contacts',
        task='api.tasks.expire_contacts_on_idle_handler',
    )


class ProcessAggregatorRequest:
    rapidpro_keys = []
    handler_keys = []
    standard_request = ''
    service_code = ''
    contact = None
    still_in_flow = False
    is_session_start = None
    handler = None

    # define a constructor they takes in a dict request from an aggregator api
    def __init__(self, aggregator_request):
        self.request_data = aggregator_request

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

    def get_expected_response(self, response_dict):
        """"
        We so far have two response formats,
        1. key-value type of response i.e (json,url-params, etc) with text and action,
        2. string response that begins with a keyword as the action
        """
        # dict has to have those keys below else keyError
        text = response_dict["text"]
        action = response_dict["action"]
        if self.handler:
            response_structure = self.handler.response_structure
            # check for aggregator response format
            res_format = self.handler.response_format
            if res_format == 1:
                # key-value
                rp_response_keys, h_response_keys = separate_keys(response_structure)
                known_keys = ['text', 'action']
                if set(known_keys) == set(rp_response_keys):
                    text_index = rp_response_keys.index("text")
                    action_index = rp_response_keys.index("action")
                    # construct response
                    h_response = {
                        h_response_keys[text_index]: text,
                        h_response_keys[action_index]: action
                    }
                    return h_response
                else:
                    raise Exception(f'The response structure "{response_structure}" has no keywords [text , action] '
                                    f'in the template definitions. ensure format is [{{text=..}},{{action=..}}]')
            else:
                # string which begins with
                h_response = f"{action.upper()} {text}"
                return h_response

    def process_handler(self):
        try:
            '''
            Lets first run the clear_timedout_sessions(), to create a task that deletes timed-out sessions
            '''
            if PeriodicTask.objects.filter(name="Clear_Timedout_sessions").exists():
                pass
            else:
                # only if the task and its scheduler have not been create yet
                clear_timedout_sessions()
            # determine service_code
            self.determine_service_code()
            request_format = self.handler.request_format
            # use defined template
            self.rapidpro_keys, self.handler_keys = separate_keys(request_format)
            # generate standard request_string to send to rapidPro
            self.generate_standard_request()
            # save contact if it doesn't exist
            self.store_contact()
            return self.standard_request
        except Exception as err:
            error_logger.exception(err)

    # call this after self.process_handler()
    @property
    def get_auth_scheme(self):

        if self.handler:
            auth_scheme = self.handler.auth_scheme
            return auth_scheme
        else:
            return "NONE"

    def determine_service_code(self):
        short_codes = Handler.objects.values_list('short_code', flat=True)
        codes = set(short_codes)
        request_values = set(self.request_data.values())
        intersect = codes.intersection(request_values)
        if len(intersect) > 0:
            self.service_code = list(intersect)[0]
        else:
            '''Lets default to the settings.DEFAULT_SHORT_CODE'''
            # check for any handlers registered with default shortcode
            if Handler.objects.filter(short_code=settings.DEFAULT_SHORT_CODE).exists():
                self.service_code = settings.DEFAULT_SHORT_CODE
            else:
                raise Exception(
                    "This aggregator most likely has no handler or a wrong shortcode was registered when creating a "
                    "handler check spelling of the code in the subsequent handler record and try again")
        # set handler is all is well
        self.handler = Handler.objects.get(short_code=self.service_code)

    def store_contact(self):
        filtered = Contact.objects.filter(urn=self.standard_request['from'])
        if filtered.exists():
            contact = Contact.objects.get(urn=self.standard_request['from'])
            self.contact = contact
        else:
            # created record
            contact = Contact.objects.create(urn=self.standard_request['from'])
            self.contact = contact
        self.is_in_flow_session()

    def is_in_flow_session(self):
        # To know whether contact is hasn't completed a flow
        # Get their latest session if any
        # check its status, if In Progress or Timed Out, then they are still in a flow.
        try:
            latest_session = USSDSession.objects.filter(contact=self.contact).latest('started_at')
            if latest_session:
                status = latest_session.status
                if status == SESSION_STATUSES['TIMED_OUT'] or status == SESSION_STATUSES['IN_PROGRESS']:
                    self.still_in_flow = True
                else:
                    self.still_in_flow = False
            else:
                self.still_in_flow = False
        except Exception as err:
            # Django object.latest() makes an exception when nothing is in the DB
            self.still_in_flow = False
            access_logger.debug(err)

    def log_session(self):
        session_id = self.standard_request['session_id']
        contact = self.contact
        # check if session id exists with
        if USSDSession.objects.filter(session_id=session_id).exists():
            # do nothing to this session
            session = USSDSession.objects.get(session_id=session_id)
            # update last visited field of this session
            session.last_access_at = timezone.now()
            session.save()
            self.is_session_start = False
        else:
            # First End all sessions attached to this urn that may already be recorded
            self.is_session_start = True
            in_progress_sessions = USSDSession.objects.filter(contact=contact, status=SESSION_STATUSES["IN_PROGRESS"])
            in_progress_sessions.update(status='Terminated', badge='warning')
            # create session
            session = USSDSession.objects.create(session_id=session_id, contact=contact, handler=self.handler)
            get_sessions()
        return session

    @property
    def get_handler(self):
        # update last accessed value
        handler = self.handler
        handler.last_accessed_at = timezone.now()
        handler.save()
        self.handler = handler
        return self.handler

    ''''
        Please call these after self.log_session()
    '''

    @property
    def is_new_session(self):
        return self.is_session_start

    @property
    def is_in_flow(self):
        return self.still_in_flow
