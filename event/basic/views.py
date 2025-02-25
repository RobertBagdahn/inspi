from __future__ import annotations

import datetime
from asyncio import Event

from django.forms import forms
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import DetailView

from .models import Event, BookingOption, EventRegistration, User


def event_main(request):
    events = Event.objects.all()
    context = {"events": events}
    print(context)
    return render(request, "event_basic_main.html", context)

def booking_options_main(request):
    options = BookingOption.objects.all()
    context = {"options": options}
    print(context)
    return render(request, "event_basic_main.html", context)

def event_detail(request):
    events = Event.objects.all()
    context = {"events": events}
    print(context)
    return render(request, "event_detail.html", context)

def event_registration(request):
    if request.method == 'POST':
        form = EventRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Speichert die Daten in der Datenbank
            return redirect('registration_success')
    else:
        form = EventRegistrationForm()
    return render(request, 'event_detail.html', {'form': form})

def registration_success(request):
    return render(request, 'registration_success.html')


class EventDetailView(DetailView):
    model = Event
    template_name = 'event_detail.html'
    context_object_name = 'event'

class EventRegistrationForm(forms.Form):
    class Meta:
        model = EventRegistration
        fields = ['first_name', 'last_name', 'email', 'event_date']
        widgets = {
            'event_date': datetime.datetime,
        }


def event_create(request):
    events = Event.objects.all()
    context = {"events": events}
    print(context)
    return render(request, "event_create.html", context)

def user_list(request):
    users = User.objects.all()  # Alle Benutzer abrufen
    return render(request, 'users.html', {'users': users})