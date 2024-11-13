from django.shortcuts import render
from .models import CustomUser
from .forms import CustomUserChangeForm
import random, string
from django.contrib.sessions.models import Session

def randomword(length):
   letters = string.ascii_lowercase
   return ''.join(random.choice(letters) for i in range(length))


def user_profile(request, username):
    try:
        user = CustomUser.objects.get(username=username)
        if not user.is_active:
            return render(request, "user-profile.html", {
                "deleted": True
            })
    except CustomUser.DoesNotExist:
        return render(request, "user-profile.html", {
            "deleted": True
        })
    return render(request, "user-profile.html", {
        "user": user,
        "deleted": False,
    })


def profile_edit(request, username):
    user = CustomUser.objects.get(username=username)
    form = CustomUserChangeForm(instance=user)

    if request.method == "POST":
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return render(request, "user-profile.html", {"user": user})

    context = {
        "user": user,
        "form": form,
    }

    return render(request, "profile-edit.html", context)


def profile_delete(request, username):
    user = CustomUser.objects.get(username=username)

    if request.method == "POST":
        user.email = "deleted"
        user.scout_display_name = randomword(20)
        user.stamm = "deleted"
        user.bund = "deleted"
        user.about_me = "deleted"
        user.is_active = False
        [s.delete() for s in Session.objects.all() if s.get_decoded().get('_auth_user_id') == user.id]
        user.save()

        return render(request, "user-profile.html", {
            "user": user,
            "deleted": True,
        })

    return render(request, "profile-delete.html", {
        "user": user,
        "deleted": False,
    })

def settings(request, username):
    user = CustomUser.objects.get(username=username)
    is_stuff = request.user.is_staff

    context = {
        "user": user,
        "is_stuff": is_stuff,
    }
    return render(request, "settings.html", context)
