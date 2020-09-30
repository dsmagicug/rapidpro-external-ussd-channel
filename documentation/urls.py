from django.urls import path
from . import views

urlpatterns = [
    path("documentation", views.index, name="documentation"),

]
