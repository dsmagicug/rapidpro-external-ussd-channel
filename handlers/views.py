from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import HandlerForm
from .models import Handler
from django.utils.safestring import mark_safe


# Create your views here.

class HandlersListView(TemplateView, LoginRequiredMixin):
    template_name = 'handlers/handler.html'
    login_url = 'login'
    raise_exception = False

    def get(self, request):
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

    def get(self, request, handler_id=None):
        if handler_id:
            if Handler.objects.filter(id=handler_id).exists():
                handler = Handler.objects.get(pk=handler_id)
                form = HandlerForm(instance=handler)
            else:
                form = HandlerForm()
                redirect('add_handler', permanent=True)
        else:
            form = HandlerForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, handler_id=None):
        if handler_id:
            handler = Handler.objects.get(pk=handler_id)
            form = HandlerForm(request.POST, instance=handler)
        else:
            form = HandlerForm(request.POST)
        if form.is_valid():
            form.save()
            self.msg = 'Saved'
            self.success = True
        else:
            self.msg = 'Form is invalid'
            self.success = False
        return render(request, self.template_name, {"form": form, "msg": self.msg, "success": self.success})
