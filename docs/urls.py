from django.urls import path
from . import views

urlpatterns = [
    path("docs", views.index, name="docs"),

]
