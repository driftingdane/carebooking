from django.shortcuts import render


def service(request):
    return render(request, "services.html")
