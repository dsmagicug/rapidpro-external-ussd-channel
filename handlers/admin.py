from django.contrib import admin
from .models import Handler
# Register your models here.
models = [
    Handler,
]
admin.site.register(models)
