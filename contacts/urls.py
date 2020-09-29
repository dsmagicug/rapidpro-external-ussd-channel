from django.urls import path
from . import views

urlpatterns = [
    path("contacts", views.contacts, name="contacts"),

]
