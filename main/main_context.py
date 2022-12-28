from django.shortcuts import render
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site


def current_site_info(request):
    current_site = get_current_site(request)
    domain = current_site.domain
    booking_title = ""
    subtitle = "Exceptional Excellent Care"
    subtext = "We provide luxury wellness care and give you a memorable experience"
    book_now = "Book a memorable time now!"

    data = {
        'domain': domain,
        'subtitle': subtitle,
        'subtext': subtext,
        'book_now': book_now,
    }
    return data
