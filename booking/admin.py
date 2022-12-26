from os import path

from django.contrib import admin
from django.shortcuts import render

from booking.models import Booking, BookingSettings


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
    "user_email", "user_name", "date", "time", "approved")
    list_filter = ("approved", "date")
    ordering = ("date", "time")
    search_fields = ("user_email", "user_name")


# @admin.register(BookingSettings)
# class BookingSettingsAdmin(admin.ModelAdmin):
#     list_display = ("max_booking_per_time", "max_booking_per_day")
#

admin.site.register(BookingSettings)
