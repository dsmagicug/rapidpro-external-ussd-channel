from django.urls import path
from . import views

urlpatterns = [
    path("send-url", views.send_url, name="send_url"),
    path("call-back", views.call_back, name="callback"),
    path("receive", views.receive, name="receive"),
    path("processor", views.processor, name="processor"),

]
