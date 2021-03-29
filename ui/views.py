from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django import template
from handlers.models import USSDSession
from rest_framework.decorators import api_view
from rest_framework.response import Response
from handlers.utils import SESSION_STATUSES
from datetime import datetime, timedelta


@login_required(login_url="/login/")
def index(request):
    sessions = USSDSession.objects.all().order_by("-last_access_at")[:200]
    context = {"sessions": sessions}
    return render(request, "index.html", context)


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('error-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('error-500.html')
        return HttpResponse(html_template.render(context, request))


@api_view(['GET'])
def graph_data(request):
    time_threshold = datetime.now() - timedelta(seconds=15)
    now = datetime.now()
    completed = USSDSession.objects.filter(last_access_at__range=[time_threshold, now]).filter(
        status=SESSION_STATUSES["COMPLETED"]).count()
    in_progress = USSDSession.objects.filter(last_access_at__range=[time_threshold, now]).filter(
        status=SESSION_STATUSES["IN_PROGRESS"]).count()
    timed_out = USSDSession.objects.filter(last_access_at__range=[time_threshold, now]).filter(
        status=SESSION_STATUSES["TIMED_OUT"]).count()
    success = completed
    timeout = timed_out
    data = [success, timeout, in_progress]
    return Response({"status": "success", "data": data}, status=200)
