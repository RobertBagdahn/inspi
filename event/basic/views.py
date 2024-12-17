from __future__ import annotations

from django.shortcuts import render

def event_main(request):
    return render(request, "event_basic_main.html")
