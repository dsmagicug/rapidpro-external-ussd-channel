from django.contrib import admin
from .models import *
# Register your models here.
models = [
    Msg,
]
admin.site.register(models)