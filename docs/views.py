from django.shortcuts import render


# Create your views here.

def index(request):
    template_name = "docs/index.html"
    return render(request, template_name)
