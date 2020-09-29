from django.contrib import admin
from .models import USSDChannel, USSDSession
# Register your models here.
models = [
    USSDChannel,
    USSDSession
]
admin.site.register(models)
