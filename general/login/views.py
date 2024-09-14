from django.shortcuts import render
from .models import CustomUser


def user_profile(request, scout_display_name):
    user = CustomUser.objects.get(scout_display_name=scout_display_name)
    return render(request, "user-profile.html", {"user": user})


def profile_edit(request, slug):
    user = CustomUser.objects.get(slug=slug)
    return render(request, "profile-edit.html", {"user": user})


def settings(request, slug):
    user = CustomUser.objects.get(slug=slug)
    return render(request, "settings.html", {"user": user})
