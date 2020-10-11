from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import USSDChannel
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

    def get(self, request):
        access_logger.info(request.META)
        channels = USSDChannel.objects.all()
        if len(channels) > 0:
            channel = channels[0]
            form = ChannelConfForm(instance=channel)
        else:
            form = ChannelConfForm()
        return render(request, self.template_name, {"form": form, "msg": self.msg, "success": self.success,
                                                    "hostname": self.hostname})

    def post(self, request):
        access_logger.info(request.META)
        try:
            channels = USSDChannel.objects.all()
            if len(channels) > 0:
                channel = channels[0]
                form = ChannelConfForm(request.POST, instance=channel)
            else:
                form = ChannelConfForm(request.POST)
            if form.is_valid():
                form.save()
                self.msg = 'Channel configurations  successfully saved.'
                self.success = True
                return redirect("/")
            else:
                self.msg = 'Form is not valid'
            return render(request, self.template_name,
                          {"form": form, "msg": self.msg, "success": self.success, "hostname": self.hostname})
        except Exception as err:
            error_logger.exception(err)