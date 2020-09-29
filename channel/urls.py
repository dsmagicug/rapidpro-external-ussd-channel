from django.urls import path
from . import views
from .views import ChannelConf

urlpatterns = [
    path("channel-config", ChannelConf.as_view(), name="channel_conf"),

]
