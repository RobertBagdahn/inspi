from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import (
    InspiGroup,
    InspiGroupNews,
    InspiGroupMembership,
    InspiGroupJoinRequest,
    InspiGroupPermission,
)
from .forms import (
    InspiGroupForm,
    InspiGroupJoinRequestForm,
    InspiGroupPermissionForm,
    InspiGroupMembershipMemberForm,
    InspiGroupMembershipAdminForm,
    JoinGroupByCodeForm,
    ManageMembershipForm,
    InspiGroupMembershipSearchFilterForm,
    MyGroupsFilterForm,
    InspiGroupNewsForm,
    GroupListFilter,
    MyRequestsFilterForm,
    InspiGroupRequestSearchFilterForm,
    ChildGroupsFilterForm,
    ParentGroupsFilterForm,
    InspiGroupAdminSearchFilterForm,
    InspiGroupAddMembershipForm,
)

User = get_user_model()


@login_required
def create_group(request):
    if request.method == "POST":
        form = InspiGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.save()
            InspiGroupMembership.objects.create(
                user=request.user, group=group, full_access=True
            )
            return redirect("group-detail-overview", group_slug=group.slug)
    else:
        form = InspiGroupForm()
    return render(request, "group/create.html", {"form": form})


@login_required
def join_group(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    # check if user is already member of group
    if group.memberships.filter(user=request.user, is_cancelled=False).exists():
        messages.warning(request, "Sie sind bereits Mitglied dieser Gruppe")
        return redirect("group-detail-overview", group_slug=group.slug)

    if request.method == "POST":
        if not group.free_to_join:
            # check if user has already requested to join group and return error message
            if InspiGroupJoinRequest.objects.filter(
                user=request.user, group=group
            ).exists():
                messages.warning(
                    request,
                    "Sie haben bereits eine Anfrage gestellt, dieser Gruppe beizutreten",
                )
                return redirect("group-detail-overview", group_slug=group.slug)
            form = InspiGroupJoinRequestForm(request.POST)
            if form.is_valid():
                join_request = form.save(commit=False)
                join_request.user = request.user
                join_request.group = group
                join_request.save()
                messages.success(request, "Anfrage zur Gruppe gestellt.")
                return redirect("group-detail-overview", group_slug=group.slug)
        else:
            InspiGroupMembership.objects.create(user=request.user, group=group)
            messages.success(request, "Erfolgreich der Gruppe beigetreten")
            return redirect("group-detail-overview", group_slug=group.slug)

    else:
        form = InspiGroupJoinRequestForm()
    return render(request, "group/join.html", {"form": form, "group": group})


@login_required
def add_user(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    if request.user not in group.editable_by_users.all():
        messages.error(request, "Sie dürfen diese Gruppe nicht bearbeiten")
        return redirect("group-detail-overview", group_slug=group.slug)

    if request.method == "POST":
        form = InspiGroupAddMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.group = group
            membership.save()
            messages.success(request, "Mitglied hinzugefügt")
            return redirect("group-detail-members", group_slug=group.slug)
    else:
        form = InspiGroupAddMembershipForm()
    return render(request, "group/add_member/main.html", {"form": form, "group": group})


@login_required
def manage_membership(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    membership = get_object_or_404(InspiGroupMembership, user=request.user, group=group)

    if request.method == "POST":
        form = ManageMembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, "Mitgliedschaft erfolgreich aktualisiert")
            return redirect("group-detail-overview", group_slug=group.slug)
    else:
        form = ManageMembershipForm(instance=membership)

    return render(
        request, "membership/manage_membership.html", {"form": form, "group": group}
    )


@login_required
def manage_requests(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)

    join_requests = InspiGroupJoinRequest.objects.filter(group=group, approved=False)
    if request.method == "POST":
        for join_request in join_requests:
            if f"approve_{join_request.id}" in request.POST:
                join_request.approved = True
                join_request.save()
                InspiGroupMembership.objects.create(user=join_request.user, group=group)
    return render(
        request,
        "request/manage_requests.html",
        {"group": group, "join_requests": join_requests},
    )


@login_required
def link_groups(request, parent_group_slug, child_group_slug):
    if request.method == "POST":
        parent_group = get_object_or_404(InspiGroup, slug=parent_group_slug)
        child_group = get_object_or_404(InspiGroup, slug=child_group_slug)
        if request.user != parent_group.created_by:
            messages.error(request, "Sie dürfen diese Gruppe nicht bearbeiten")
            return redirect("group-detail-overview", group_slug=parent_group.slug)
        InspiGroupPermission.objects.create(
            group=parent_group, linked_group=child_group
        )
        return redirect("group-detail-overview", group_slug=parent_group.slug)


@login_required
def create_permission(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    if request.user not in group.editable_by_users.all():
        messages.error(request, "Sie dürfen diese Gruppe nicht bearbeiten")
        return redirect("group-detail-overview", group_slug=group.slug)

    if request.method == "POST":
        form = InspiGroupPermissionForm(request.POST)

        if form.is_valid():
            permission = form.save(commit=False)
            permission.group = group
            permission.save()
            return redirect("group-detail-manage", group_slug=group.slug)
    else:
        form = InspiGroupPermissionForm()
    return render(request, "permission/create.html", {"form": form, "group": group})


@login_required
def manage_permissions(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)

    if request.user not in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)

    permission = get_object_or_404(InspiGroupPermission, group=group)

    context = {"group": group, "permission": permission}

    return render(
        request,
        "membership/manage_permissions.html",
        context,
    )


@login_required
def leave_group(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)

    # get all
    memberships = InspiGroupMembership.objects.filter(
        user=request.user, group=group, is_cancelled=False
    )

    for membership in memberships:
        membership.is_cancelled = True
        membership.date_cancelled = timezone.now()
        membership.cancel_by = request.user
        membership.save()

    return redirect("group-dashboard")

def edit_membership_admin(request, membership_id):
    membership = get_object_or_404(InspiGroupMembership, id=membership_id)

    group = membership.group
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    if request.method == "POST":
        form = InspiGroupMembershipMemberForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            return redirect("group-detail-overview", group_slug=group.slug)
    else:
        form = InspiGroupMembershipAdminForm(instance=membership)
    return render(
        request, "membership/create_membership.html", {"form": form, "group": group}
    )

def edit_membership_member(request, membership_id):
    membership = get_object_or_404(InspiGroupMembership, id=membership_id)
    group = membership.group
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    if request.method == "POST":
        form = InspiGroupMembershipMemberForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            return redirect("group-detail-overview", group_slug=group.slug)
    else:
        form = InspiGroupMembershipMemberForm(instance=membership)
    return render(
        request, "membership/create_membership.html", {"form": form, "group": group}
    ) 

def remove_membership(request, membership_id):
    membership = get_object_or_404(InspiGroupMembership, id=membership_id)
    group = membership.group
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    membership.is_cancelled = True
    membership.date_cancelled = timezone.now()
    membership.cancel_by = request.user
    messages.success(request, "Mitgliedschaft entfernt")
    return redirect("group-detail-overview", group_slug=group.slug)


@login_required
def approve_membership(request, membership_id):
    membership = get_object_or_404(InspiGroupMembership, id=membership_id)
    group = membership.group
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    membership.approved = True
    membership.save()
    return redirect("manage_requests", group_slug=group.slug)

@login_required
def group_detail_news(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)

    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()
    news = InspiGroupNews.objects.filter(group=group).order_by("-created_at")
    
    if is_member == False and is_admin == False:
        messages.error(request, "Du kann nicht auf die News dieser Gruppe zugreifen. Da du kein Mitglied bist.")
        return redirect("group-detail-overview", group_slug=group.slug)
    
    if is_admin == False: 
        news = news.filter(is_visible=True)

    context = {
        "group": group,
        "news": news,
        "is_admin": is_admin,
        "is_member": is_member,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "News", "active": True},
        ],
    }
    return render(request, "group/details/news/main.html", context)

@login_required
def create_group_news(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    is_admin = request.user in group.editable_by_users.all()
    
    if is_admin == False:
        messages.error(request, "Du kannst keine News erstellen, da du kein Admin dieser Gruppe bist.")
        return redirect("group-detail-news", group_slug=group.slug)
    
    if request.method == "POST":
        form = InspiGroupNewsForm(request.POST)
        if form.is_valid():
            news = form.save(commit=False)
            news.group = group
            news.created_by = request.user
            form.save()
            return redirect("group-detail-news", group_slug=group.slug)
    else:
        form = InspiGroupNewsForm()
    return render(request, "group/details/news/create_edit.html", {"form": form, "create": True, "group": group})

@login_required
def edit_group_news(request, group_slug, news_id):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    news = get_object_or_404(InspiGroupNews, id=news_id)
    is_admin = request.user in group.editable_by_users.all()
    
    if is_admin == False:
        messages.error(request, "Du kannst keine News bearbeiten, da du kein Admin dieser Gruppe bist.")
        return redirect("group-detail-news", group_slug=group.slug)
    
    if request.method == "POST":
        form = InspiGroupNewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()
            return redirect("group-detail-news", group_slug=group.slug)
    else:
        form = InspiGroupNewsForm(instance=news)
    return render(request, "group/details/news/create_edit.html", {"form": form, "create": False, "group": group})

@login_required
def delete_group_news(request,  group_slug, news_id):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    instance = get_object_or_404(InspiGroupNews, id=news_id)
    is_admin = request.user in group.editable_by_users.all()
    
    if is_admin == False:
        return HttpResponse(status_code=403, content="Du kannst keine News löschen, da du kein Admin dieser Gruppe bist.")
    
    instance.delete()

    return HttpResponse("")

@login_required
def group_detail_overview(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    memberships = InspiGroupMembership.objects.filter(group=group).count()
    editable_by_users = group.editable_by_users.count()
    open_requests = InspiGroupJoinRequest.objects.filter(group=group)
    news = InspiGroupNews.objects.filter(group=group).filter(is_visible=True).order_by("-created_at")
    news_count = news.count()
    news = news.last()

    # hide geheime field join_code is_visible
    if not request.user in group.editable_by_users.all():
        group.join_code = None
        group.is_visible = False

    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()

    context = {
        "group": group,
        "membership_kpi": f"{memberships} Personen",
        "admin_kpi": f"{editable_by_users} Personen",
        "open_requests": open_requests,
        "is_admin": is_admin,
        "news": news,
        "news_count": news_count,
        "is_member": is_member,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Übersicht", "active": True},
        ],
    }
    return render(request, "group/details/overview/main.html", context)


@login_required
def group_detail_requests(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    memberships = InspiGroupMembership.objects.filter(group=group)
    editable_by_users = group.editable_by_users.all()
    open_requests = InspiGroupJoinRequest.objects.filter(group=group)
    linked_parent_groups = group.parent_groups.all()

    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()

    search_filter_form = InspiGroupRequestSearchFilterForm()

    context = {
        "group": group,
        "memberships": memberships,
        "admins": editable_by_users,
        "linked_parent_groups": linked_parent_groups,
        "open_requests": open_requests,
        "is_admin": is_admin,
        "is_member": is_member,
        "search_filter_form": search_filter_form,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Anfragen", "active": True},
        ],
    }
    return render(request, "group/details/requests/main.html", context)


@login_required
def group_detail_members(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    memberships = InspiGroupMembership.objects.filter(group=group)
    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()

    if request.GET:
        search_filter_form = InspiGroupMembershipSearchFilterForm(request.GET)
    else:
        search_filter_form = InspiGroupMembershipSearchFilterForm(
            initial={"search": "", "is_cancelled": False, "is_not_cancelled": True}
        )

    # filter memberships is_cancelled
    if search_filter_form.is_valid():
        if search_filter_form.cleaned_data.get("is_cancelled"):
            memberships = memberships.filter(is_cancelled=True)
        if search_filter_form.cleaned_data.get("is_not_cancelled"):
            memberships = memberships.filter(is_cancelled=False)

    paginator = Paginator(memberships, 10)  # Show 10 memberships per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "group": group,
        "page_obj": page_obj,
        "search_filter_form": search_filter_form,
        "is_admin": is_admin,
        "is_member": is_member,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Mitglieder", "active": True},
        ],
    }
    return render(request, "group/details/members/main.html", context)


@login_required
def group_detail_admins(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    editable_by_users = group.editable_by_users.all()
    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()

    search_filter_form = InspiGroupAdminSearchFilterForm(request.GET)

    if search_filter_form.is_valid():
        editable_by_users = editable_by_users.filter(
            username__icontains=search_filter_form.cleaned_data.get("search", "")
        )

    paginator = Paginator(editable_by_users, 10)  # Show 10 admins per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "form": search_filter_form,
        "group": group,
        "is_admin": is_admin,
        "is_member": is_member,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Admins", "active": True},
        ],
    }
    return render(request, "group/details/admins/main.html", context)


@login_required
def group_detail_manage(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()

    context = {
        "group": group,
        "is_admin": is_admin,
        "is_member": is_member,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Verwalten", "active": True},
        ],
    }
    return render(request, "group/details/manage/main.html", context)


@login_required
def group_detail_child_groups(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()
    child_groups = group.subgroups.all()

    form_filter_and_form = ChildGroupsFilterForm()

    paginator = Paginator(child_groups, 10)  # Show 10 child groups per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "group": group,
        "page_obj": page_obj,
        "is_admin": is_admin,
        "is_member": is_member,
        "form": form_filter_and_form,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Untergruppen", "active": True},
        ],
    }
    return render(request, "group/details/child_groups/main.html", context)


@login_required
def group_detail_parent_groups(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    is_admin = request.user in group.editable_by_users.all()
    is_member = group.memberships.filter(user=request.user, is_cancelled=False).exists()
    parent_groups = group.parent_groups.all()

    form_filter_and_form = ParentGroupsFilterForm()

    paginator = Paginator(parent_groups, 10)  # Show 10 parent groups per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "group": group,
        "page_obj": page_obj,
        "is_admin": is_admin,
        "is_member": is_member,
        "form": form_filter_and_form,
        "breadcrumbs": [
            {"name": "Gruppen", "url": "/group/group-list"},
            {"name": group.name, "url": f"/group/detail/{group.slug}/overview"},
            {"name": "Elterngruppen", "active": True},
        ],
    }
    return render(request, "group/details/parent_groups/main.html", context)


@login_required
def delete_group(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)

    # check if group has any members and return error message
    if group.memberships.exists():
        messages.error(
            request,
            "Die Gruppe hat Mitglieder. Bitte entfernen Sie alle Mitglieder, bevor Sie die Gruppe löschen",
        )
        return redirect("group-detail-overview", group_slug=group.slug)

    # delete group with set is_cancelled to True
    group.is_cancelled = True
    group.date_cancelled = timezone.now()
    group.cancel_by = request.user

    return redirect("dashboard")


@login_required
def create_membership(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    if request.method == "POST":
        form = InspiGroupMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.group = group
            membership.save()
            return redirect("group-detail-overview", group_slug=group.slug)
    else:
        form = InspiGroupMembershipForm()
    return render(
        request, "membership/create_membership.html", {"form": form, "group": group}
    )


@login_required
def update_membership(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    if request.method == "POST":
        form = InspiGroupMembershipForm(request.POST)
        if form.is_valid():
            membership = form.save(commit=False)
            membership.group = group
            membership.save()
            return redirect("group-detail-overview", group_slug=group.slug)
    else:
        form = InspiGroupMembershipForm(
            instance=get_object_or_404(
                InspiGroupMembership, group=group, user=request.user
            )
        )
    return render(
        request, "membership/create_membership.html", {"form": form, "group": group}
    )


@login_required
def dashboard(request):
    memberships = InspiGroupMembership.objects.filter(user=request.user)

    open_requests = InspiGroupJoinRequest.objects.filter(
        user=request.user, approved=None
    )
    # all is_visible groups where you are not member
    joinable_groups = (
        InspiGroup.objects.filter(is_visible=True)
        .exclude(inspigroupmembership__user=request.user)
        .filter(free_to_join=True)
    )
    kpi_memberships = memberships.filter(is_cancelled=False).count()
    kpi_adminships = InspiGroup.objects.filter(editable_by_users=request.user).count()
    kpi_free_to_join = joinable_groups.count()
    kpi_open_request = open_requests.count()

    return render(
        request,
        "dashboard/main.html",
        {
            "can_join_group": joinable_groups.exists(),
            "kpi_memberships": f"{kpi_memberships} Gruppen",
            "kpi_adminships": f"{kpi_adminships} Gruppen",
            "kpi_free_to_join": f"{kpi_free_to_join} Gruppen",
            "kpi_open_request": f"{kpi_open_request} Anfragen",
        },
    )


@login_required
def my_groups(request):
    memberships = InspiGroupMembership.objects.filter(user=request.user)

    if not request.GET:
        request.GET = request.GET.copy()
        request.GET["is_not_cancelled"] = "True"
    search_filter_form = MyGroupsFilterForm(request.GET)
    if search_filter_form.is_valid():
        memberships = memberships.filter(
            user__username__icontains=search_filter_form.cleaned_data.get("search", "")
        )
        if search_filter_form.cleaned_data.get("is_cancelled"):
            memberships = memberships.filter(is_cancelled=True)
        if search_filter_form.cleaned_data.get("is_not_cancelled"):
            memberships = memberships.filter(is_cancelled=False)

    paginator = Paginator(memberships, 10)  # Show 10 memberships per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    form = MyGroupsFilterForm(request.GET)
    return render(
        request,
        "my-groups/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )


@login_required
def my_requests_admin(request):
    # filter all reqeusts where user is admin
    requests = InspiGroupJoinRequest.objects.filter(group__editable_by_users=request.user)
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
        "my-requests/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )


@login_required
def group_list(request):
    if not request.GET:
        request.GET = request.GET.copy()
        # request.GET['is_not_cancelled'] = 'True'
    search_filter_form = GroupListFilter(request.GET)
    if search_filter_form.is_valid():
        groups = InspiGroup.objects.filter(
            is_visible=True or request.user in group.editable_by_users.all()
        )
        groups = groups.filter(
            name__icontains=search_filter_form.cleaned_data.get("search", "")
        )
        if search_filter_form.cleaned_data.get("is_cancelled"):
            groups = groups.filter(is_cancelled=True)
        if search_filter_form.cleaned_data.get("is_not_cancelled"):
            groups = groups.filter(is_cancelled=False)

    if search_filter_form.cleaned_data.get("free_to_join"):
        groups = groups.filter(free_to_join=True)

    if search_filter_form.cleaned_data.get("is_visible"):
        groups = groups.filter(is_visible=True)

    if search_filter_form.cleaned_data.get("is_member"):
        groups = groups.filter(
            inspigroupmembership__is_cancelled=False,
            inspigroupmembership__user=request.user,
        )

    if search_filter_form.cleaned_data.get("is_not_member"):
        member_groups = groups.filter(
            inspigroupmembership__is_cancelled=False,
            inspigroupmembership__user=request.user,
        )
        groups = groups.exclude(id__in=member_groups)

    if search_filter_form.cleaned_data.get("is_admin"):
        groups = groups.filter(editable_by_users=request.user)

    # add is_member property to each group
    for group in groups:
        group.is_member = group.memberships.filter(
            user=request.user, is_cancelled=False
        ).exists()

    # add is_admin property to each group
    for group in groups:
        group.is_admin = request.user in group.editable_by_users.all()

    paginator = Paginator(groups, 10)  # Show 10 groups per page.
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    form = GroupListFilter(request.GET)
    return render(
        request,
        "group/list/main.html",
        {
            "page_obj": page_obj,
            "form": form,
        },
    )


@login_required
def join_group_by_code(request):
    # get query parameter join_code
    join_code_get = request.GET.get("join_code", None)
    group = None

    if (
        not InspiGroup.objects.filter(join_code=join_code_get).exists()
        and join_code_get
    ):
        messages.error(request, "Ungültiger Beitrittscode")
        # redirce without get parameter
        return redirect(request.path_info)

    if request.method == "POST":
        join_code = request.POST.get("join_code")

        # check if group exists
        if not InspiGroup.objects.filter(join_code=join_code).exists():
            messages.error(request, "Ungültiger Beitrittscode")
            return redirect("join-group-by-code")

        group = InspiGroup.objects.get(join_code=join_code)

        # check if user is already member of group
        if group.memberships.filter(user=request.user, is_cancelled=False).exists():
            messages.warning(request, "Sie sind bereits Mitglied dieser Gruppe")
            return redirect("group-detail-overview", group_slug=group.slug)

        # check if user has already requested to join group and return error message
        if InspiGroupJoinRequest.objects.filter(
            user=request.user, group=group
        ).exists():
            messages.warning(
                request,
                "Sie haben bereits eine Anfrage gestellt, dieser Gruppe beizutreten",
            )
            return redirect("group-dashboard")

        InspiGroupMembership.objects.create(user=request.user, group=group)
        return redirect("group-detail-overview", group_slug=group.slug)

    if join_code_get:
        group = get_object_or_404(InspiGroup, join_code=join_code_get)

    form = JoinGroupByCodeForm(
        initial={"join_code": join_code_get, "user": request.user}
    )

    context = {"group": group, "user": request.user, "form": form}

    return render(request, "group/join-by-code.html", context)


@login_required
def membership_detail(request, membership_id):
    membership = get_object_or_404(InspiGroupMembership, id=membership_id)
    group = get_object_or_404(InspiGroup, id=membership.group.id) 

    is_admin = request.user in group.editable_by_users.all()
    is_member = membership.user == request.user

    items = [
        {"title": "Gruppe", "value": membership.group},
        {"title": "Mitglied", "value": membership.user},
    ]
    if not membership.is_cancelled:
        items.append(
            {"title": "Lesezugriff", "value": membership.read_access}
        )
        items.append(
            {"title": "Vollzugriff", "value": membership.full_access},
        )
        items.append(
            {"title": "Persönliche Daten teilen", "value": membership.share_all_personal_data},
        )
        items.append(
            {"title": "Eigene persönliche Daten teilen", "value": membership.share_own_personal_data},
        )
    
    # add if is_cancelled is True
    if membership.is_cancelled:
        items.append(
            {"title": "Storniert?", "value": membership.is_cancelled},
        )
        items.append(
            {"title": "Stornierungsdatum", "value": membership.date_cancelled},
        )
        items.append(
            {"title": "Storniert von", "value": membership.cancel_by},
        )
    return render(
        request,
        "membership/membership_detail.html",
        {
            "membership": membership,
            "items": items,
            "is_admin": is_admin,
            "is_member": is_member,
        },
    )


@login_required
def approve_request(request, request_id):
    join_request = get_object_or_404(InspiGroupJoinRequest, id=request_id)
    group = join_request.group
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    InspiGroupMembership.objects.create(user=join_request.user, group=group)
    join_request.approved = True
    join_request.date_checked = timezone.now()
    join_request.user_checked_by = request.user
    join_request.save()
    messages.success(request, "Anfrage akzeptiert")
    return redirect("manage-requests", group_slug=group.slug)


@login_required
def decline_request(request, request_id):
    join_request = get_object_or_404(InspiGroupJoinRequest, id=request_id)
    group = join_request.group
    if request.user in group.editable_by_users.all():
        return redirect("group-detail-overview", group_slug=group.slug)
    join_request.approved = False
    join_request.date_checked = timezone.now()
    join_request.user_checked_by = request.user
    join_request.save()
    messages.success(request, "Anfrage abgelehnt")
    return redirect("manage-requests", group_slug=group.slug)


@login_required
def request_detail(request, request_id):
    join_request = get_object_or_404(InspiGroupJoinRequest, id=request_id)
    group = get_object_or_404(InspiGroup, id=join_request.group.id) 

    is_admin = request.user in group.editable_by_users.all()
    is_member = join_request.user == request.user

    items = [
        {"title": "Gruppe", "value": join_request.group},
        {"title": "Mitglied", "value": join_request.user},
        {"title": "Datum", "value": join_request.date_requested},
    ]

    if join_request.approved is not None:
        items.append({"title": "Genehmigt", "value": join_request.approved})
        items.append({"title": "Datum überprüft", "value": join_request.date_checked})
        items.append({"title": "Überprüft von", "value": join_request.user_checked_by})

    return render(
        request,
         "request/request_detail.html",
        {
            "join_request": join_request,
            "items": items,
            "is_admin": is_admin,
            "is_member": is_member,
        },
    )

   


@login_required
def edit_group(request, group_slug):
    group = get_object_or_404(InspiGroup, slug=group_slug)

    if not group.memberships.filter(user=request.user, is_cancelled=False).exists():
        messages.error(request, "Sie dürfen diese Gruppe nicht bearbeiten")
        return redirect("group-detail-overview", group_slug=group.slug)

    if request.method == "POST":
        form = InspiGroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("group-detail-overview", group_slug=group.slug)

    form = InspiGroupForm(instance=group)
    return render(request, "group/update.html", {"form": form, "group": group})


@login_required
def search_results_view(request, group_slug):
    query = request.GET.get("search", "")
    group = get_object_or_404(InspiGroup, slug=group_slug)

    group_members = group.memberships.filter(is_cancelled=False)

    all_data = User.objects.exclude(id__in=group_members.values_list("user", flat=True))
    if query and len(query) > 0:
        all_data = all_data.filter(username__icontains=query)
        context = {"data": all_data[:10], "count": all_data.count()}
    else:
        all_data = []
        context = {"data": all_data, "count": -1}

    return render(request, "group/add_member/search_results.html", context)
