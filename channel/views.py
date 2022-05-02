from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from handlers.models import USSDChannel
from .forms import ChannelConfForm

import socket

from core.utils import access_logger, error_logger


# Create your views here.


class ChannelConf(LoginRequiredMixin, TemplateView):
    template_name = 'channel/conf.html'
    login_url = 'login'
    raise_exception = False
    success = False
    msg = None
    hostname = socket.gethostname()

    def get(self, request, *args, **kwargs):
        access_logger.info(request)
        if "channel_id" in kwargs:
            channel_id = kwargs['channel_id']
            if USSDChannel.objects.filter(pk=channel_id).exists():
                channel = USSDChannel.objects.get(pk=channel_id)
            else:
                return redirect(reverse('channel_conf'))
            form = ChannelConfForm(instance=channel)
        else:
            form = ChannelConfForm()
        return render(request, self.template_name, {"form": form, "msg": self.msg, "success": self.success,
                                                    "hostname": self.hostname})

    def post(self, request, *args, **kwargs):
        access_logger.info(request)
        try:
            if "channel_id" in kwargs:
                channel_id = kwargs['channel_id']
                channel = USSDChannel.objects.get(pk=channel_id)
                form = ChannelConfForm(request.POST, instance=channel)
            else:
                form = ChannelConfForm(request.POST)
            if form.is_valid():
                form.save()
                self.msg = 'Channel configurations  successfully saved.'
                self.success = True
                return redirect(reverse("channel_list"))
            else:
                self.msg = 'Form is not valid'
            return render(request, self.template_name,
                          {"form": form, "msg": self.msg, "success": self.success, "hostname": self.hostname})
        except Exception as err:
            error_logger.exception(err)


class ChannelListView(LoginRequiredMixin, TemplateView):
    template_name = 'channel/channels.html'
    login_url = 'login'
    raise_exception = False

    def get(self, request, *args, **kwargs):
        channels = USSDChannel.objects.all()
        context = dict(channels=channels)
        return render(request, self.template_name, context)
