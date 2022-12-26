from django.urls import path

from . import views
from .views import (BookingApproveView, BookingCreateWizardView,
                    BookingDeleteView, BookingHomeView, BookingListView,
                    BookingSettingsView, get_available_time, DaysDeleteView)

app_name = 'booking'

urlpatterns = [
    # path('thanks/', views.thanks, name="thanks"),
    path('booking_disabled/', views.booking_disabled, name="booking_disabled"),
    path('', BookingCreateWizardView.as_view(), name="create_booking"),

    path('admin/dashboard/', BookingHomeView.as_view(), name="admin_dashboard"),
    path('admin/list/', BookingListView.as_view(), name="booking_list"),
    path('admin/settings/', BookingSettingsView.as_view(), name="booking_settings"),
    path('admin/disable_dates/', views.disable_dates, name="disable_dates"),
    path('admin/<pk>/delete/',
         BookingDeleteView.as_view(), name="booking_delete"),
    path('<pk>/delete/', DaysDeleteView.as_view(), name="days_delete"),
    path('admin/<pk>/approve/',
         BookingApproveView.as_view(), name="booking_approve"),

    path('get-available-time/', get_available_time, name="get_available_time"),
]
