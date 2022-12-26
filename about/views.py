from django.shortcuts import render
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site


def about(request):
    current_site = get_current_site(request)
    domain = current_site.domain
    data = {
        'domain': domain,
    }
    return render(request, "about.html", data)
