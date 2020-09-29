from rest_framework import serializers
from .models import USSDSession


class SessionSerializer(serializers.ModelSerializer):
    contact = serializers.ReadOnlyField(source='contact.urn')
    handler = serializers.ReadOnlyField(source='handler.aggregator')

    class Meta:
        model = USSDSession
        fields = "__all__"
