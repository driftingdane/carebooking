from django.shortcuts import render

from main.models import SiteInfo


def home(request):
    return render(request, "index.html")
