from rest_framework.decorators import api_view
from rest_framework.response import Response
import redis
import json
import requests
from ast import literal_eval
import secrets
from websocket import create_connection
from msgs.utils import MESSAGE_TYPE
from handlers.utils import ProcessAggregatorRequest, get_sessions
from channel.models import USSDChannel, USSDSession

from core.utils import access_logger, error_logger

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
        to = request.data['to']
        _from = request.data['from']
        actions = ['request', 'request']
        action = secrets.choice(actions)
        msg = f"{request.data['text']}"
        content = {"from": _from, "action": action, "responseString": msg}
        # decrement key1
        key1 = f"MO_MT_KEY_{_from}"
        key2 = f"MSG_KEY_{_from}"
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
        urn = standard_request_string['from']
        msg_type = MESSAGE_TYPE.OUTGOING
        # TODO tell if its first string
        print(standard_request_string)
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
        # receive_url = "http://localhost:5000/adaptor/receive"
        # req = requests.post(receive_url, json.dumps(rapid_pro_request), headers=HEADERS)
        req = requests.post(receive_url, rapid_pro_request, headers=HEADERS)
        if req.status_code == 200:
            # TODO log message in database
            # increment key1
            r.incr(key1)
            r.expire(key1, 30)  # expire key1 after 30s
            data = r.blpop(key2, channel.timeout_after)  # wait for configured time for rapidPro instance
            # TODO when data is back, check if its last message and update session status accordingly
            # assume it the final message in the session
            USSDSession.objects.filter(session_id=current_session_id).update(status="Completed", badge="success")
            if data:
                response = literal_eval(data[1].decode("utf-8"))
            else:
                # pop key2 to avoid sync issues
                USSDSession.objects.filter(session_id=current_session_id).update(status="Timed Out", badge="danger")
                error_logger.debug(f"Response timed out for redis key {key2}")
                r.lpop(key2)
                response = {"responseString": "Response timed out", "action": "end"}
        else:
            response = {"responseString": "External Application unreachable", "action": "end"}
        return Response(response, status=200)
    except Exception as err:
        error_logger.exception(err)
        response = {"responseString": "External Application unreachable", "action": "end"}
        return Response(response, status=500)


@api_view(['POST', 'GET', 'PUT'])
def receive(request):
    # access_logger.info(str(request.META))
    print(request.META)
    try:
        url = "http://localhost:5000/adaptor/processor"
        req = requests.post(url, json.dumps(request.data), headers=HEADERS)
        status = req.status_code
        if status == 200:
            return Response(dict(message="Receive got it"), status=200)
        else:
            return Response(dict(message="Some error"), status=200)
    except Exception as err:
        error_logger.exception(err)
        print(err)


@api_view(['POST'])
def processor(request):
    data = request.data
    phrases = [
        "What month did you start your last period?\n1.Jan\n2.Feb\n"
    ]
    text = secrets.choice(phrases)
    to = "rapidPro"
    _from = data['from']
    response = {"text": text, "to": to, "from": _from, "status": "waiting"}
    # call send url
    url = "http://localhost:5000/adaptor/send-url"
    req = requests.post(url, json.dumps(response), headers=HEADERS)
    if req.status_code == 200:
        return Response(response, status=200)
