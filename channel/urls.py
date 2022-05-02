from django.urls import path
from . import views
from .views import ChannelConf, ChannelListView

urlpatterns = [
    path("channel-config", ChannelConf.as_view(), name="channel_conf"),
    path("channel-config/channel/<int:channel_id>", ChannelConf.as_view(), name="edit_channel"),
    path("channel-list", ChannelListView.as_view(), name="channel_list")

]
