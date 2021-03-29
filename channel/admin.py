from django.contrib import admin
from .models import USSDChannel

# Register your models here.
models = [
    USSDChannel,
]
admin.site.register(models)
