from django.urls import path
from .views import login_view,  profile, enable_disable, invite
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("profile", profile, name="profile"),
    path("activate", enable_disable, name="enable_disable"),
    path("invite", invite, name="invite")
]
