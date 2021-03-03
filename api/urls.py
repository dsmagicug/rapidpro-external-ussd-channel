from django.urls import path
from . import views
from .views import CallBack
urlpatterns = [
    path("send-url", views.send_url, name="send_url"),
    path("call-back", CallBack.as_view(), name="callback"),
    path("clear-sessions", views.clear_sessions, name="clear_sessions"),
    path("test-call", CallBack.as_view(), name="test_callback" )
]
