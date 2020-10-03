from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, SignUpForm
from django.contrib.auth.decorators import login_required
from core.utils import access_logger
from django.utils import timezone
from django.http import JsonResponse


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                access_logger.info(f"User {request.user.username} logged in at {timezone.now()}")
                return redirect("/")
            else:
                msg = 'Invalid credentials'
                access_logger.debug(f"User {username} login Failed at {timezone.now()}")
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            msg = 'User created.'
            success = True
            # return redirect("/login/")
        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})


@login_required(login_url="/login/")
def profile(request):
    template_name = "accounts/profile.html"
    ME = request.user
    form = SignUpForm(instance=ME)
    users = User.objects.all()
    msg = None
    if request.method == "POST":
        action = request.POST['action']
        if action == "update":
            username = request.POST['username']
            email = request.POST['email']
            ME.username = username
            ME.email = email
            ME.save()
            form = SignUpForm(instance=ME)
            msg = "Profile information successfully updated."
        else:
            # update password
            old_password = request.POST["old-password"]
            new_password = request.POST["new-password"]
            username = request.user.username
            user = authenticate(username=username, password=old_password)
            if user:
                ME.set_password(new_password)
                ME.save()
                login(request, ME)
                status = "success"
                message = f"Password successfully changed.</b>"
            else:
                # wrong password
                status = "error"
                message = "Wrong old password supplied"
            return JsonResponse({"status": status, "message": message})
    context = dict(users=users, form=form, msg=msg)
    return render(request, template_name, context)
