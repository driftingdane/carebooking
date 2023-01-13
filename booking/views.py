import datetime
from typing import Dict, List

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.datetime_safe import date
from django.views.generic import (DeleteView, ListView, TemplateView,
                                  UpdateView, View)
from formtools.wizard.views import SessionWizardView

from booking.forms import (BookingCustomerForm, BookingDateForm,
                           BookingSettingsForm, BookingTimeForm, BookingDisableDaysForm)
from booking.models import Booking, BookingSettings, DisabledDays
from booking.settings import (BOOKING_BG, BOOKING_DESC, BOOKING_DISABLE_URL,
                              BOOKING_SUCCESS_REDIRECT_URL, BOOKING_TITLE, BOOKING_NOW,
                              PAGINATION)
from booking.utils import BookingSettingMixin


# # # # # # #
# Admin Part
# # # # # # #

class BookingHomeView(BookingSettingMixin, TemplateView):
  model = Booking
  template_name = "booking/admin/dashboard.html"

  def get_context_data(self, **kwargs):
    today = date.today()
    seven_day_before = today - datetime.timedelta(days=7)
    seven_day_ahead = today + datetime.timedelta(days=7)
    context = super().get_context_data(**kwargs)
    context["weekly_bookings"] = Booking.objects.filter(date__lt=seven_day_ahead).order_by(
      "-date", "time")[:10]
    # context["today_bookings"] = Booking.objects.filter(start__lte=timezone.now().replace(hour=0, minute=0, second=0), end__gte=timezone.now().replace(hour=23, minute=59, second=59)).order_by(
    #     "-date", "time")[:10]
    context["today_bookings"] = Booking.objects.filter(date__lte=timezone.now(), date__exact=today).order_by(
      "-date", "time")[:10]
    context["pending_bookings"] = Booking.objects.filter(
      approved=False).order_by("-date", "time")[:10]
    context["approved_bookings"] = Booking.objects.filter(
      approved=True).order_by("-date", "time")[:10]
    return context


class BookingListView(BookingSettingMixin, ListView):
  model = Booking
  template_name = "booking/admin/booking_list.html"
  paginate_by = PAGINATION


class BookingSettingsView(BookingSettingMixin, UpdateView):
  form_class = BookingSettingsForm
  template_name = "booking/admin/booking_settings.html"
  success_url = reverse_lazy("booking:booking_settings")

  def get_object(self, **kwargs):
    return BookingSettings.objects.filter().first()

  def get_success_url(self):
    return reverse("booking:booking_settings")


def disable_dates(request):
  obj = BookingSettings.objects.filter().first()
  dis_days = DisabledDays.objects.all()
  if request.method == 'POST':
    dis_form = BookingDisableDaysForm(request.POST)
    if dis_form.is_valid():
      disable_days = dis_form.cleaned_data
      dis_days = disable_days['disable_days']
      fields = dis_days.split(",")
      for x in fields:
        print(x)
        x.replace(",", "")
        created = DisabledDays.objects.create(
          disable_dates=x,
          settings=obj,
        )
      return HttpResponse("Success")
  else:
    dis_form = BookingDisableDaysForm()
    data = {
      'dis_form': dis_form,
      'obj': obj,
      'dis_days': dis_days,
    }
    return render(request, "booking/admin/disable_days.html", data)


class DaysDeleteView(BookingSettingMixin, DeleteView):
  model = DisabledDays
  success_url = reverse_lazy("booking:disable_dates")
  template_name = "booking/admin/disable_days.html"


class BookingDeleteView(BookingSettingMixin, DeleteView):
  model = Booking
  success_url = reverse_lazy("booking:booking_list")
  queryset = Booking.objects.filter()


class BookingApproveView(BookingSettingMixin, View):
  model = Booking
  success_url = reverse_lazy("booking:booking_list")
  fields = ("approved",)

  def post(self, request, *args, **kwargs):
    booking = get_object_or_404(Booking, pk=self.kwargs.get("pk"))
    booking.approved = True
    booking.save()
    # Send mail
    send_mail(
      'Din booking#' + str(booking.booking_no) + ' fra CareShop.dk',
      'Hej ' + booking.user_name + '. Tak for din booking. Du vil modtaget endnu en email med bekræftelse.',
      'lingostack@gmail.com',
      [booking.user_email],
      fail_silently=False
    )
    return redirect(self.success_url)


# # # # # # # #
# Booking Part
# # # # # # # #
BOOKING_STEP_FORMS = (
  ('Date', BookingDateForm),
  ('Time', BookingTimeForm),
  ('User Info', BookingCustomerForm)
)


class BookingCreateWizardView(SessionWizardView):
  template_name = "booking/user/booking_wizard.html"
  form_list = BOOKING_STEP_FORMS

  def get_context_data(self, form, **kwargs):
    context = super().get_context_data(form=form, **kwargs)
    progress_width = "6"
    if self.steps.current == 'Time':
      context["get_available_time"] = get_available_time(
        self.get_cleaned_data_for_step('Date')["date"])
      progress_width = "30"
    if self.steps.current == 'User Info':
      progress_width = "75"

    context.update({
      'booking_settings': BookingSettings.objects.first(),
      "progress_width": progress_width,
      "booking_bg": BOOKING_BG,
      "description": BOOKING_DESC,
      "title": BOOKING_TITLE,
      "book_now": BOOKING_NOW

    })
    return context

  def render(self, form=None, **kwargs):
    # Check if Booking is Disable
    form = form or self.get_form()
    context = self.get_context_data(form=form, **kwargs)

    if not context["booking_settings"].booking_enable:
      return redirect(BOOKING_DISABLE_URL)

    return self.render_to_response(context)

  def done(self, form_list, **kwargs):
    data = dict((key, value) for form in form_list for key, value in form.cleaned_data.items())
    booking = Booking.objects.create(**data)
    if BOOKING_SUCCESS_REDIRECT_URL:
      return redirect(BOOKING_SUCCESS_REDIRECT_URL)

    return render(self.request, 'booking/user/booking_done.html', {
      "progress_width": "100",
      "booking_id": booking.booking_no,
      "booking_bg": BOOKING_BG,
      "description": BOOKING_DESC,
      "title": BOOKING_TITLE
    })


def add_delta(time: datetime.time, delta: datetime.datetime) -> datetime.time:
  # transform to a full datetime first
  return (datetime.datetime.combine(
    datetime.date.today(), time
  ) + delta).time()


def get_available_time(date: datetime.date) -> List[Dict[datetime.time, bool]]:
  """
  Check for all available time for selected date
  The times should start_time and end_time
  If the time already is taken -> is_taken = True
  """
  booking_settings = BookingSettings.objects.first()
  existing_bookings = Booking.objects.filter(
    date=date).values_list('time')
  next_time = booking_settings.start_time
  time_list = []
  while True:
    is_taken = any([x[0] == next_time for x in existing_bookings])
    time_list.append(
      {"time": ":".join(str(next_time).split(":")[:-1]), "is_taken": is_taken})
    next_time = add_delta(next_time, datetime.timedelta(
      minutes=int(booking_settings.period_of_each_booking)))
    if next_time > booking_settings.end_time:
      break

  return time_list


def booking_disabled(request):
  return render(request, "booking/booking_disabled.html")



def ghjk():
  return