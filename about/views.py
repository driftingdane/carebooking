from django.shortcuts import render


def about(request):
    data = {

    }
    return render(request, "about.html", data)
