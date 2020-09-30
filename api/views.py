from rest_framework.decorators import api_view
from rest_framework.response import Response
import redis
import json
import requests
from ast import literal_eval
import secrets
from websocket import create_connection
from handlers.utils import ProcessAggregatorRequest, RP_RESPONSE_FORMAT, RP_RESPONSE_STATUSES
from channel.models import USSDChannel, USSDSession
from core.utils import access_logger, error_logger
from django.http import QueryDict
from ast import literal_eval

# Create your views here.

HEADERS = requests.utils.default_headers()
HEADERS.update(
    {
        'Content-type': 'application/x-www-form-urlencoded',
        # 'Content-type': 'application/json',
    }
)

r = redis.Redis(host='localhost', port=6379, db=0)


def push_ussd(payload):
    try:
        ws = create_connection("ws://localhost:5000/ws/demo")
        ws.send(json.dumps(payload))
        ws.close()
        return True
    except Exception as err:
        error_logger.exception(err)
        return False


@api_view(['POST'])
def send_url(request):
    # access_logger.info(request.META)
    try:
        if isinstance(request.data, QueryDict):  # for application/x-www-form-urlencoded
            data = request.data
            content = data.dict()
        else:
            content = request.data  # for application/json
        # decrement key1
        to = content['to']
        key1 = f"MO_MT_KEY_{to}"
        key2 = f"MSG_KEY_{to}"
        key1_val = int(r.decr(key1))
        if key1_val >= 0:
            r.lpush(key2, str(content))
        else:
            msg_extras = dict(msg_type="Outgoing", status="Received")
            content = request.data
            content.update(msg_extras)
            push = push_ussd(content)
            # reset key to 1
            r.set(key1, 0, ex=10)
            if push:
                # TODO inform RapidPro of the success
                pass
            else:
                # TODO inform RapidPro of the failure
                pass
        return Response({"message": "success"}, status=200)
    except Exception as err:
        error_logger.exception(err)


@api_view(['POST', 'GET', 'PUT'])
def call_back(request):
    # access_logger.info(str(request.META))
    try:
        request_dict = literal_eval(json.dumps(request.data['info']))  # from GCE
        # request_dict = literal_eval(json.dumps(request.data))
        sr = ProcessAggregatorRequest(request_dict)
        standard_request_string = sr.process_handler()
        current_session_id = sr.log_session()

        handler = sr.get_handler()
        end_action = handler.signal_end_string
        reply_action = handler.signal_reply_string

        urn = standard_request_string['from']
        # TODO tell if its first string
        rapid_pro_request = {
            "from": urn,
            "text": standard_request_string["text"]
        }
        # create redis keys
        key1 = f"MO_MT_KEY_{urn}"
        r.set(key1, 1)  # proven necessary or else
        key2 = f"MSG_KEY_{urn}"
        """""Channel details """""
        # first fetch all since you are not sure of the id (in cases
        # where once channel was deleted, (impossible to do that within the app though)
        channels = USSDChannel.objects.all()
        channel = channels[0] if len(channels) > 0 else None
        if channel is None:
            raise Exception("Could not continue without a channel, configure one first and try again")

        # receive_url is used to send msgs to rapidpro
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
                    # mark session complete
                    USSDSession.objects.filter(session_id=current_session_id).update(status="Completed",
                                                                                     badge="success")
                    action = end_action
                new_format = dict(text=text, action=action)
                response = sr.get_expected_response(new_format)
            else:
                # pop key2 to avoid sync issues
                USSDSession.objects.filter(session_id=current_session_id).update(status="Timed Out", badge="danger")
                error_logger.debug(f"Response timed out for redis key {key2}")
                r.lpop(key2)
                res_format = dict(text="Response timed out", action=end_action)
                response = sr.get_expected_response(res_format)
        else:
            res_format = dict(text="External Application unreachable", action=end_action)
            response = sr.get_expected_response(res_format)
        return Response(response, status=200)
    except Exception as err:
        error_logger.exception(err)
        response = {"responseString": "External Application unreachable", "action": "end"}
        return Response(response, status=500)
