from django.contrib import admin
from .models import Contact
# Register your models here.
models = [
    Contact,
]
admin.site.register(models)
