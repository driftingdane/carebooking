from django.contrib import admin
from about.models import About


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = (
        "title", "info")
