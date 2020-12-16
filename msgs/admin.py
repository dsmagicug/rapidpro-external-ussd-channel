from django.contrib import admin
from .models import *
models = [
    Msg,
]
admin.site.register(models)