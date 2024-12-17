from __future__ import annotations

from datetime import timezone

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.shortcuts import render



from event.registration.models import Registration

def registrations(request):
    return render(request, "activity/dashboard/main.html")