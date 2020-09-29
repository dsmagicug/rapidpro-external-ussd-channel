from django.contrib import admin
from .models import *
# Register your models here.
models = [
    Tester,
]
admin.site.register(models)