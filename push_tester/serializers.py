from rest_framework import serializers
from .models import Tester
from msgs.models import Msg


class TesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tester
        fields = "__all__"


class MsgSerializer(serializers.ModelSerializer):
    class Meta:
        model = Msg
        fields = "__all__"
