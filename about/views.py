from django.shortcuts import render

from about.models import About


def about(request):
    about = About.objects.first()
    data = {
        'title': about.title,
        'about': about.info,
        'img': about.image,

    }
    return render(request, "about.html", data)
