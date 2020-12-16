'''
This module  uses web sockets together with a an android app to found at 
https://github.com/ekeeya/ussd-push-simulator
Remember to change the constants in /src/utils before generating the APK
'''

from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Tester
from msgs.models import Msg
from .serializers import TesterSerializer, MsgSerializer
from handlers.utils import standard_urn


@api_view(['POST'])
def demo_register(request):
    try:
        posted_data = request.data
        msisdn = posted_data['msisdn']
        if Tester.objects.filter(msisdn=msisdn).exists():
            tester = Tester.objects.get(msisdn=msisdn)
        else:
            device_unique_id = posted_data['deviceUniqueID']
            tester = Tester.objects.create(msisdn=msisdn, device_unique_id=device_unique_id)
        serializer = TesterSerializer(tester)
        tester_json = serializer.data
        return Response({"status": "success", "message": f"{msisdn} has been successfully registered.Enjoy the Demo",
                         "data": tester_json}, status=200)
    except Exception as err:
        print(err)
        return Response({"status": "error", "message": str(err)}, status=500)


@api_view(['GET'])
def get_tester(request, msisdn):
    try:
        standard_msisdn = standard_urn(msisdn)
        tester = Tester.objects.get(msisdn=standard_msisdn)
        serializer = TesterSerializer(tester)
        tester_json = serializer.data
        return Response({"status": "success", "data": tester_json}, status=200)
    except Exception as err:
        print(err)
        return Response({"status": "error", "message": str(err)}, status=400)


@api_view(['POST'])
def record_message(request):
    post_data = request.data
    msg_type = post_data['msgType']
    msg_body = post_data['msgBody']
    status = post_data['status']
    msisdn = post_data['msisdn']
    sender = post_data['sender']
    receiver = post_data['receiver']
    msg = Msg.objects.create(msg_type=msg_type, msg_body=msg_body, status=status,
                             contact=msisdn, sender=sender, receiver=receiver)
    serializer = MsgSerializer(msg)
    msg_data = serializer.data
    return Response({"status": "success", "data": msg_data}, status=200)


@api_view(['GET'])
def get_msgs(request, msisdn):
    try:
        msgs = Msg.objects.filter(contact=msisdn)
        serializer = MsgSerializer(msgs, many=True)
        messages = serializer.data
        return Response({
            "status": 'success',
            "data": messages,
        }, status=200)
    except Exception as err:
        print(err)
        return Response({"status": "error", "message": str(err)}, status=400)


@api_view(['GET', 'POST'])
def socket_data(request):
    try:
        return Response(dict(message="Receive got it"), status=200)
    except Exception as err:
        print(err)
