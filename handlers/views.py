from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from .forms import HandlerForm
from .models import Handler
from core.utils import access_logger, error_logger


class HandlersListView(TemplateView, LoginRequiredMixin):
    template_name = 'handlers/handler.html'
    login_url = 'login'
    raise_exception = False

    def get(self, request):
        access_logger.info(str(request))
        handlers = Handler.objects.all()
        return render(request, self.template_name, {"handlers": handlers})


class RegisterHandlerView(View, LoginRequiredMixin):
    template_name = 'handlers/add_handler.html'
    login_url = 'login'
    raise_exception = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.success = None
        self.msg = None
        self.isNewHandler = True
        self.aggregator = None
        self.token = None
        self.auth_scheme = None

    # will be used to authenticate aggregator requests
    def create_auth_user(self, aggregator=None):
        if aggregator:
            user = User.objects.create_user(username=aggregator)
        else:
            user = User.objects.create_user(username=self.aggregator)
        user.is_staff = False
        user.save()
        # create a token for this user
        token = Token.objects.create(user=user)
        self.token = token

    def get_auth_token(self):
        # get corresponding user in order to obtain the auth token
        if User.objects.filter(username=self.aggregator).exists():
            user = User.objects.get(username=self.aggregator)
            if user:
                token = Token.objects.get(user=user)
                self.token = token.key
        else:
            self.create_auth_user()

    def get(self, request, handler_id=None):
        access_logger.info(str(request))
        try:
            if handler_id:
                if Handler.objects.filter(id=handler_id).exists():
                    handler = Handler.objects.get(pk=handler_id)
                    self.auth_scheme = handler.auth_scheme
                    self.aggregator = handler.aggregator
                    form = HandlerForm(instance=handler)
                    self.get_auth_token()
                else:
                    form = HandlerForm()
                    redirect('add_handler', permanent=True)
            else:
                form = HandlerForm()
            return render(request, self.template_name,
                          {"form": form, "token": self.token, "auth_scheme": self.auth_scheme})

        except Exception as err:
            error_logger.exception(err)

    def post(self, request, handler_id=None):
        access_logger.info(request)
        try:
            if handler_id:
                handler = Handler.objects.get(pk=handler_id)
                self.auth_scheme = handler.auth_scheme
                self.aggregator = handler.aggregator
                self.get_auth_token()
                self.isNewHandler = False
                form = HandlerForm(request.POST, instance=handler)
            else:
                form = HandlerForm(request.POST)
            if form.is_valid():
                form.save()
                # create new non-staff user and assign them an auth token
                if self.isNewHandler:
                    aggregator = form.cleaned_data["aggregator"]
                    self.create_auth_user(aggregator)

                self.msg = 'Saved'
                self.success = True
            else:
                self.msg = 'Form is invalid'
                self.success = False
            return render(request, self.template_name,
                          {"form": form, "msg": self.msg, "token": self.token, "success": self.success,
                           "auth_scheme": self.auth_scheme})

        except Exception as err:
            error_logger.exception(err)
