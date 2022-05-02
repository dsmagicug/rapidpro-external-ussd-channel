from django.contrib import admin
from .models import Handler, USSDSession
# Register your models here.
models = [
    Handler,
    USSDSession
]
admin.site.register(models)
