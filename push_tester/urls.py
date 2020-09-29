from django.urls import path
from . import views

urlpatterns = [
    path("demo_register/", views.demo_register, name="demo_register"),
    path('demo_tester/<str:msisdn>', views.get_tester, name='demo_tester'),
    path('demo_store_msg', views.record_message, name='demo_store_msg'),
    path('demo_msgs/<str:msisdn>', views.get_msgs, name="demo_msgs"),
    path('receive/<str:msisdn>', views.get_msgs, name="demo_msgs"),
]
