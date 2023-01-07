from django.shortcuts import render
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site

from main.models import SiteInfo


def current_site_info(request):
    current_site = get_current_site(request)
    main = SiteInfo.objects.first()
    domain = current_site.domain
    booking_title = ""
    book_now = "Book a memorable time now!"
    print(main.description)
    print(main.subtitle)
    print(main.image)
    print(main.alt_text)

    data = {
        'domain': domain,
        'subtitle': main.subtitle,
        'book_now': book_now,
        'name': main.name,
        'image': main.image,
        'alt_text': main.alt_text,
        'desc': main.description,

    }
    return data
