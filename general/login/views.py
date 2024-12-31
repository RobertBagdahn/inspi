from django.shortcuts import render
from .models import CustomUser
from .forms import CustomUserChangeForm, InspiGroupAdminSearchFilterForm
from group.forms import MyRequestsFilterForm
import random, string
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required

from group.models import InspiGroup, InspiGroupMembership, InspiGroupJoinRequest, InspiGroupPermission
from django.core.paginator import Paginator


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


def user_detail_overview(request, username):
    user = CustomUser.objects.get(username=username)

    search_filter_form = InspiGroupAdminSearchFilterForm(request.GET)

    # get all inspi groups
    kpi_membershps = InspiGroupMembership.objects.filter(user=user, is_cancelled=False).count()

    items_basic = [
        {"title": "Anzeigename", "value": user.scout_display_name},
        {"title": "E-Mail", "value": user.email},
        {"title": "Registrierungsdatum", "value": user.date_joined},
        {"title": "Letzter Login", "value": user.last_login},
    ]
    if user.is_staff:
        items_basic.append(
            {"title": "Ist Admin", "value": user.is_staff}
        )

    if user.is_superuser:
        items_basic.append(
            {"title": "Ist Superuser", "value": user.is_superuser}
        )

    if user.person:
        items_personal = [
            {"title": "Vorname", "value": user.person.first_name},
            {"title": "Nachname", "value": user.person.last_name},
            {"title": "Geburtstag", "value": user.person.birthday},
            {"title": "Handynummer", "value": user.mobile},
            {"title": "Adresse", "value": user.person.address},
            {"title": "Adresszusatz", "value": user.person.address_supplement},
            {"title": "Postleitzahl", "value": user.person.zip_code},
            {"title": "Stadt", "value": user.person.city},
            {"title": "Geschlecht", "value": user.person.get_gender_display()},
            {"title": "Essgewohnheiten", "value": user.person.get_eat_habits_display()},
            {"title": "Über mich", "value": user.person.about_me},
            {"title": "Stamm", "value": user.person.stamm},
            {"title": "Bund", "value": user.person.bund},
        ]
    else:
        items_personal = []

    # editable  when stuff or user is the same as the user
    editable = False
    if request.user.is_staff or request.user == user:
        editable = True


    return render(request, "user-detail/overview/main.html", {
        "user": user,
        "deleted": False,
        "items_basic": items_basic,
        "items_personal": items_personal,
        "kpi_membershps": kpi_membershps,
        "editable": editable,
        "search_filter_form": search_filter_form
    })

def user_detail_manage(request, username):
    user = CustomUser.objects.get(username=username)

    return render(request, "user-detail/manage/main.html", {
        "user": user,
        "deleted": False,
    })


def user_detail_memberships(request, username):
    user = CustomUser.objects.get(username=username)
    memberships = InspiGroupMembership.objects.filter(user=user)
    search_filter_form = InspiGroupAdminSearchFilterForm(request.GET)

    paginator = Paginator(memberships, 10)  # Show 10 memberships per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "user": user,
        "deleted": False,
        "page_obj": page_obj,
        "search_filter_form": search_filter_form,
    }

    return render(request, "user-detail/memberships/main.html", context)


def user_detail_person(request, username):
    user = CustomUser.objects.get(username=username)

    return render(request, "user-detail/person/main.html", {
        "user": user,
        "deleted": False,
    })


def user_dashboard(request):
    user = CustomUser.objects.get(username=request.user.username)

    return render(request, "user-dashboard/main.html", {
        "user": user,
        "deleted": False,
    })


def user_list(request):
    users = CustomUser.objects.all()

    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "user-list/main.html", {
        "page_obj": page_obj,
        "users": users,
    })



@login_required
def user_detail_my_requests_user(request, username):
    user = CustomUser.objects.get(username=username)
    # check if user is the same as the user in the url or is staff or superuser
    if not request.user.is_staff and not request.user.is_superuser and request.user != user:
        return render(request, "403.html")
    requests = InspiGroupJoinRequest.objects.filter(user=user)
    form = MyRequestsFilterForm(request.GET)

    if form.is_valid():
        requests = requests.filter(
            group__name__icontains=form.cleaned_data.get("search", "")
        )
        if form.cleaned_data.get("approved"):
            requests = requests.filter(approved=True)
        if form.cleaned_data.get("not_approved"):
            requests = requests.filter(approved=False)

    paginator = Paginator(requests, 10)  # Show 10 requests per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "user-detail/my-requests/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )
