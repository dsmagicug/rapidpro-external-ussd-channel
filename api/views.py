from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings

import redis
import requests
from websocket import create_connection
from ast import literal_eval
import json

from handlers.utils import ProcessAggregatorRequest, RP_RESPONSE_FORMAT, RP_RESPONSE_STATUSES, standard_urn, \
    SESSION_STATUSES, get_channel, RP_RESPONSE_CONTENT_TYPES
from core.utils import error_logger
from channel.models import USSDSession

HEADERS = requests.utils.default_headers()
HEADERS.update(
    {
        'Content-type': 'application/x-www-form-urlencoded',  # for now this is what works with rapidPro
    }
)

# TODO a singleton for this so that we have only one redis connection for all requests
r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


def changeSessionStatus(session, status, badge):
    session.status = status
    session.badge = badge
    session.save()


def push_ussd(payload, request):
    try:
        host = request.get_host()
        ws = create_connection(f"ws://{host}/ws/demo")
        ws.send(json.dumps(payload))
        ws.close()
        return True
    except Exception as err:
        error_logger.exception(err)
        return False


@api_view(['POST'])
def send_url(request):
    try:
        if "CONTENT_TYPE" in request.META:
            content_type = "CONTENT_TYPE"
        else:
            content_type = "HTTP_CONTENT_TYPE"
        if request.META[content_type] == RP_RESPONSE_CONTENT_TYPES["URL_ENCODED"]:
            data = request.data
            content = data.dict()
        else:
            content = request.data
        # decrement key1
        to = content['to_no_plus']
        key1 = f"MO_MT_KEY_{to}"
        key2 = f"MSG_KEY_{to}"
        key1_val = int(r.decr(key1))
        if key1_val >= 0:
            r.lpush(key2, str(content))
        else:
            action = "end"
            # code here is currently temporary
            if content["session_status"] == RP_RESPONSE_STATUSES["waiting"]:
                action = "request"
            msg_extras = dict(msg_type="Outgoing", status="Received", action=action)
            content.update(msg_extras)
            push = push_ussd(content,request)
            # reset key to 1
            r.set(key1, 0, ex=10)
        return Response({"message": "success"}, status=200)
    except Exception as err:
        error_logger.exception(err)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def call_back(request):
    # CHECK METHOD USED
    if request.META["REQUEST_METHOD"] == "GET":
        data = request.GET
        request_data = data.dict()
    else:
        request_data = request.data
    try:
        sr = ProcessAggregatorRequest(request_data)
        standard_request_string = sr.process_handler()
        current_session = sr.log_session()
        is_new_session = sr.is_new_session
        still_in_flow = sr.is_in_flow
        handler = sr.get_handler
        end_action = handler.signal_end_string
        reply_action = handler.signal_reply_string
        urn = standard_request_string['from']
        channel = get_channel()
        if channel is None:
            raise Exception("Could not continue without a channel, configure one first and try again")

        if is_new_session:
            text = " " if still_in_flow else channel.trigger_word
        else:
            text = standard_request_string["text"]
        allowed_urn = standard_urn(urn)

        rapid_pro_request = {
            "from": allowed_urn,
            "text": text
        }
        # create redis keys
        key1 = f"MO_MT_KEY_{allowed_urn}"
        r.set(key1, 1)  # proven necessary or else
        key2 = f"MSG_KEY_{allowed_urn}"
        """""Channel details """""

        # receive_url is used to send msgs to rapidPro
        receive_url = channel.rapidpro_receive_url
        # req = requests.post(receive_url, json.dumps(rapid_pro_request), headers=HEADERS)
        req = requests.post(receive_url, rapid_pro_request, headers=HEADERS)
        if req.status_code == 200:
            # increment key1
            r.incr(key1)
            r.expire(key1, 30)  # expire key1 after 30s
            data = r.blpop(key2, channel.timeout_after)  # wait for configured time for rapidPro instance
            if data:
                feedback = literal_eval(data[1].decode("utf-8"))  # from RapidPro
                text = feedback[RP_RESPONSE_FORMAT['text']]
                status = feedback[RP_RESPONSE_FORMAT['session_status']]
                if status == RP_RESPONSE_STATUSES['waiting']:
                    action = reply_action
                else:
                    # mark session complete and give it a green badge
                    changeSessionStatus(current_session, SESSION_STATUSES['COMPLETED'], 'success')
                    action = end_action
                new_format = dict(text=text, action=action)
                response = sr.get_expected_response(new_format)
            else:
                # mark session timed out and give it a red badge
                changeSessionStatus(current_session, SESSION_STATUSES['TIMED_OUT'], 'danger')
                error_logger.debug(f"Response timed out for redis key {key2}")
                res_format = dict(text="Response timed out", action=end_action)
                response = sr.get_expected_response(res_format)
        else:
            changeSessionStatus(current_session, SESSION_STATUSES['TIMED_OUT'], 'danger')
            res_format = dict(text="External Application unreachable", action=end_action)
            error_logger.exception(req.content)
            response = sr.get_expected_response(res_format)
        return Response(response, status=200)
    except Exception as err:
        error_logger.exception(err)
        response = {"responseString": "External Application unreachable", "action": "end"}
        return Response(response, status=500)


@api_view(['GET'])
def clear_sessions(request):
    try:
        # delete all sessions
        USSDSession.objects.all().delete()
        response = dict(status="success")
        return Response(response, status=200)
    except Exception as error:
        error_logger.exception(error)
        response = dict(status="error", message=f"{str(error)}")
        return Response(response, status=500)
