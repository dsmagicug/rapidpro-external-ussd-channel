from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User, auth
from .forms import LoginForm, SignUpForm
from django.contrib.auth.decorators import login_required
from core.utils import access_logger
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.utils.safestring import mark_safe
import random, string
from django.core.mail import send_mail
from django.conf import settings


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
    users = User.objects.exclude(username=ME.username)
    msg = None
    if request.method == "POST":
        action = request.POST['action']
        if action == "update":
            username = request.POST['username']
            email = request.POST['email']
            ME.username = username
            ME.email = email
            ME.save()
            login(request, ME)
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


@csrf_exempt
def enable_disable(request):
    user_id = request.POST["user_id"]
    is_active = request.POST["is_active"]
    activate = True if is_active == "true" else False
    user = User.objects.get(pk=user_id)
    user.is_active = activate
    user.save()
    action = "enabled" if activate else "disabled"
    message = f"User {user.username} has been {action}"
    return JsonResponse(dict(status="success", message=message))


def invite(request):
    email = request.POST["email"]
    try:
        validate_email(email)  # produced an exception if wrong format
        # Create account with email supplied
        status = "success"
        username = email.split("@")[0]
        password = "".join(random.choices(string.ascii_uppercase + string.digits, k=15))
        new_user = User.objects.create_user(username=username, email=email, password=password)
        msg = mark_safe(
            f"Hello\nYou have been invited by {request.user.email} to RapidPro External USSG channel.\nVisit {settings.HOST} and login with " f"the following credentials\n<tr><td><b>Username</b></td><td>{username}</td></tr><tr><td><b>Password</b" f"></td><td>{password}</td></tr>\nPlease change your password upon logging in")
        new_user.save()
        # TODO SMTP to send mail
        send_mail(
            'RapidPro External USSD channel invitation',
            msg,
            settings.EMAIL_HOST_USER,
            ['ekeeya@ds.co.ug'],
            fail_silently=False,
        )
        message = mark_safe(f"Invite to <b>{email}</b> has been sent")
    except Exception as err:
        message = str(err)
        status = "error"

    return JsonResponse(dict(status=status, message=message))
