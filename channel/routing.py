from django.urls import path

from . import consumers
from push_tester.consumers import PushConsumer

websocket_urlpatterns = [
    path('ws/sessions', consumers.LiveSessionsConsumer),
    path('ws/demo', PushConsumer),
]