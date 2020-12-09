from django.urls import path
from . import views

urlpatterns = [
    path("send-url", views.send_url, name="send_url"),
    path("call-back", views.call_back, name="callback"),
    path("clear-sessions", views.clear_sessions, name="clear_sessions")
]
