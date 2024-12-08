import json
from pydantic import Field, BaseModel
from django.shortcuts import render


from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from formtools.wizard.views import SessionWizardView, CookieWizardView
from django.db.models import Q
from django.core.mail import send_mail
from general.login.models import CustomUser
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDay

from activity.activity.service.admin.ai_suggestion import get_ai_suggestion


from django.shortcuts import get_object_or_404
from django.utils.formats import date_format

from django.contrib import messages

from tracking.models import Visitor

from activity.activity import models as activity_models
from activity.activity import choices as activity_choices
from .forms import (
    ActivityUpdateForm,
    RatingForm,
    TopicForm,
    ChoicesForm,
    MainTextForm,
    HeaderTextForm,
    CreatorForm,
    ImageForm,
    MaterialForm,
    UnkownForm,
    StatusSearchFrom,
    CommentForm,
    SearchForm,
    EventOfWeekForm,
    SearchDetailForm,
    CommentAdminForm,
    EmotionAdminForm,
    TopicAdminForm,
    AiForm,
)

from django.http import Http404
from django.core.paginator import Paginator

from django.template import loader


def list(request):
    user = request.user
    status = request.GET.get("status", activity_choices.StatusSearchChoices.ALL)
    query = request.GET.get("query", "")
    page_num = request.GET.get("page", 1)

    if status != activity_choices.StatusSearchChoices.ALL:
        activities = activity_models.Activity.objects.filter(status=status)
    else:
        activities = activity_models.Activity.objects.all()

    if query:
        activities = activities.filter(title__icontains=query)

    if user and not user.is_authenticated:
        activities = activities.filter(
            Q(status=activity_choices.StatusSearchChoices.PUBLISHED)
        )

    if user and user.is_authenticated and not user.is_staff and not user.is_superuser:
        activities = activities.filter(
            Q(status=activity_choices.StatusSearchChoices.PUBLISHED)
            | Q(authors=user.id)
        )

    activities = activities.order_by("-created_at")
    # set status default to '0'
    form = SearchForm(request.GET or None, initial={"status": "0"})

    tags = activity_models.Topic.objects.all()

    context = {
        "activities": activities,
        "form": form,
        "tags": tags,
        "user": user,
    }
    return render(request, "activity/dashboard/main.html", context)


def detail(request, activity_id):
    comment_form = CommentForm()
    related_activities = activity_models.Activity.objects.all().order_by("?")[:4]
    try:
        activity = activity_models.Activity.objects.get(pk=activity_id)
        activity.update_views()

    except activity_models.Activity.DoesNotExist:
        raise Http404("Activity does not exist")

    return render(
        request,
        "activity/detail.html",
        {
            "activity": activity,
            "can_edit": activity.is_allowed_to_edit(request.user),
            "comment_form": comment_form,
            "related_activities": related_activities,
        },
    )


def main_view(request, topic_id=None, scout_level_id=None):
    query = request.GET.get("q", "")
    page_num = request.GET.get("page", 1)
    activities_raw = activity_models.Activity.objects.filter(
        title__icontains=query
    ).order_by("-created_at")
    if topic_id:
        activities_raw = activities_raw.filter(topics__id=topic_id)
        selected_topic = activity_models.Topic.objects.get(id=topic_id)
    else:
        selected_topic = None

    if scout_level_id:
        activities_raw = activities_raw.filter(scout_levels__id=scout_level_id)
        selected_scout_level = activity_models.ScoutLevelChoice.objects.get(
            id=scout_level_id
        )
    else:
        selected_scout_level = None

    topics = activity_models.Topic.objects.all()

    activities_raw = activities_raw.filter(
        status=activity_choices.StatusSearchChoices.PUBLISHED
    )

    newest_activities = activities_raw.order_by("-created_at")[:4]
    famous_activities = activities_raw.order_by("-view_count")[:4]
    random_activities = activities_raw.order_by("?")[:8]

    context = {
        "newest_activities": newest_activities,
        "famous_activities": famous_activities,
        "random_activities": random_activities,
        "topics": topics,
        "selected_topic": selected_topic,
        "selected_scout_level": selected_scout_level,
        "count": activity_models.Activity.objects.count(),
    }
    return render(request, "activity/main-view.html", context)


def _load_activities(request, category_name, category_id):
    if category_name == "topic":
        activities_raw = activity_models.Activity.objects.filter(
            topics__id=category_id
        ).order_by("?")
        selected_category = activity_models.Topic.objects.get(id=category_id)
        selected_category_str = selected_category.name

    if category_name == "scout-level":
        activities_raw = activity_models.Activity.objects.filter(
            scout_levels__id=category_id
        ).order_by("?")
        selected_category = activity_models.ScoutLevelChoice.objects.get(id=category_id)
        selected_category_str = selected_category.name

    if category_name == "activity-type":
        activities_raw = activity_models.Activity.objects.filter(
            activity_types__id=category_id
        ).order_by("?")
        selected_category = activity_models.ActivityType.objects.get(id=category_id)
        selected_category_str = selected_category.name

    if category_name == "random":
        activities_raw = activity_models.Activity.objects.all().order_by("?")
        selected_category_str = "Inspirierend"

    if category_name == "newest":
        activities_raw = activity_models.Activity.objects.all().order_by("-created_at")
        selected_category_str = "Neueste"

    if category_name == "trend":
        activities_raw = activity_models.Activity.objects.all().order_by("-view_count")
        selected_category_str = "Trend"

    activities_raw = activities_raw.filter(
        status=activity_choices.StatusSearchChoices.PUBLISHED
    )

    paginator = Paginator(activities_raw, per_page=24)
    page_num = request.GET.get("page", 1)
    page_object = paginator.get_page(page_num)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    return page_object, selected_category_str


def main_category_view(request, category_name, category_id):
    page_object, selected_category_str = _load_activities(
        request, category_name, category_id
    )
    context = {
        "activities": page_object,
        "selected_category": selected_category_str,
        "category_name": category_name,
        "category_id": category_id,
    }
    return render(request, "activity/main-category.html", context)


def search(request):
    q = request.GET.get("query", "")

    # clean q
    q = q.strip()
    q = q.replace("  ", " ")

    sort = request.GET.get("sort", "0")
    scout_levels = request.GET.getlist("scout_levels")
    activity_types = request.GET.getlist("activity_types")
    locations = request.GET.getlist("locations")
    times = request.GET.getlist("times")
    topics = request.GET.getlist("topics")
    costs_rating = request.GET.get("costs_rating")
    difficulty = request.GET.get("difficulty")
    execution_time = request.GET.get("execution_time")
    preparation_time = request.GET.get("preparation_time")
    status = request.GET.get("status", "0")

    items = activity_models.Activity.objects.all()

    if sort == "0":
        items = items.order_by("-created_at")
    elif sort == "1":
        items = items.order_by("created_at")
    elif sort == "2":
        # likes
        items = items.order_by("-created_at")
    elif sort == "3":
        # comments
        items = items.order_by("-created_at")
    elif sort == "4":
        items = items.order_by("?")

    if q != "":
        items = items.filter(
            Q(title__icontains=q)
            | Q(authors__scout_display_name__icontains=q)
            | Q(topics__name__icontains=q)
            | Q(summary__icontains=q)
            | Q(description__icontains=q)
            | Q(material_list__material_name__name__icontains=q)
        )

    if scout_levels:
        items = items.filter(scout_levels__id__in=scout_levels)

    if activity_types:
        items = items.filter(activity_types__id__in=activity_types)

    if locations:
        items = items.filter(locations__id__in=locations)

    if times:
        items = items.filter(times__id__in=times)

    if topics:
        items = items.filter(topics__id__in=topics)

    if costs_rating:
        items = items.filter(costs_rating=costs_rating)

    if difficulty:
        items = items.filter(difficulty=difficulty)

    if execution_time:
        items = items.filter(execution_time=execution_time)

    if preparation_time:
        items = items.filter(preparation_time=preparation_time)

    if status != "0":
        items = items.filter(status=str(status))

    items = items.distinct()

    page_num = request.GET.get("page", 1)
    paginator = Paginator(items, per_page=12)
    page_object = paginator.get_page(page_num)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(page_num)
    form = SearchDetailForm(
        request.GET or None,
        initial={
            "sort": "0",
            "status": "0",
        },
    )

    context = {
        "activities": page_object,
        "form": form,
    }
    return render(request, "activity/search/main.html", context)


def list_load_activities_view(request, category_name, category_id):
    page_object, selected_category_str = _load_activities(
        request, category_name, category_id
    )

    context = {
        "activities": page_object,
        "selected_category": selected_category_str,
        "category_name": category_name,
        "category_id": category_id,
    }
    return render(request, "activity/partials/all-activities.html", context)


def all_items(request):
    query = request.GET.get("q", "")
    page_num = request.GET.get("page", 1)
    activities_raw = activity_models.Activity.objects.filter(
        title__icontains=query
    ).order_by("-created_at")
    categories = activity_models.Tag.objects.filter(category_id=9)

    paginator = Paginator(activities_raw, per_page=10)
    page_object = paginator.get_page(page_num)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "activities": page_object,
        "page_object": page_object,
        "categories": categories,
    }
    return render(request, "activity/overview.html", context)


def faq(request):
    template = loader.get_template("footer/faq.html")
    context = {}
    return HttpResponse(template.render(context, request))


def update(request, activity_id):
    activity = activity_models.Activity.objects.get(id=activity_id)
    form = ActivityUpdateForm(request.POST or None, instance=activity)
    return render(request, "activity/update.html", {"activity": activity, "form": form})


TEMPLATES = {
    "intro": "activity/create/full/0-intro-step.html",
    "main-text": "activity/create/full/1-main-text-step.html",
    "header-text": "activity/create/full/2-header-text-step.html",
    "rating": "activity/create/full/3-rating-step.html",
    "topic": "activity/create/full/4-tag-step.html",
    "choices": "activity/create/full/4-tag-step.html",
    "material": "activity/create/full/5-material-step.html",
    "image": "activity/create/full/6-image-step.html",
    "creator": "activity/create/full/5-creator-step.html",
}


class ContactWizard(CookieWizardView):

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        return context

    def get_form_initial(self, step):
        initial = self.initial_dict.get(step, {})
        if step == "rating":
            initial.update(
                {
                    "costs_rating": 1,
                    "difficulty": 1,
                    "execution_time": 1,
                    "preparation_time": 1,
                }
            )
        if step == "creator":
            initial.update(
                {
                    "status": 1,
                }
            )
        if step == "topic":
            initial.update({})

        return initial

    def done(self, form_list, form_dict, **kwargs):

        # full
        if len(form_list) == 7:
            activity = activity_models.Activity.objects.create(
                description=form_dict["main-text"].cleaned_data["description"],
                title=form_dict["header-text"].cleaned_data["title"],
                summary=form_dict["header-text"].cleaned_data["summary"],
                summary_long=form_dict["header-text"].cleaned_data["summary_long"],
                costs_rating=form_dict["rating"].cleaned_data["costs_rating"],
                difficulty=form_dict["rating"].cleaned_data["difficulty"],
                execution_time=form_dict["rating"].cleaned_data["execution_time"],
                preparation_time=form_dict["rating"].cleaned_data["preparation_time"],
                status=form_dict["creator"].cleaned_data["status"],
            )

            topics = form_dict["topic"].cleaned_data["topics"]

            scout_levels = form_dict["choices"].cleaned_data["scout_levels"]
            activity_types = form_dict["choices"].cleaned_data["activity_types"]
            locations = form_dict["choices"].cleaned_data["locations"]
            times = form_dict["choices"].cleaned_data["times"]

            # topics = [int(topic) for topic in topics]
            activity_types = [int(activity_type.id) for activity_type in activity_types]
            locations = [int(location.id) for location in locations]
            times = [int(time.id) for time in times]

            activity.topics.add(*topics)
            activity.scout_levels.add(*scout_levels)
            activity.activity_types.add(*activity_types)
            activity.locations.add(*locations)
            activity.times.add(*times)

            if "created_by_email" in form_dict["creator"].cleaned_data:
                activity.created_by_email = form_dict["creator"].cleaned_data[
                    "created_by_email"
                ]
                activity.created_by_name = form_dict["creator"].cleaned_data[
                    "created_by_name"
                ]

            if "authors" in form_dict["creator"].cleaned_data:
                activity.authors.add(*form_dict["creator"].cleaned_data["authors"])

            activity.save()

        # short
        if len(form_list) == 3:

            activity = activity_models.Activity.objects.create(
                title="Noch nicht gesetzt",
                description=form_dict["main-text"].cleaned_data["description"],
            )

            # if form_dict["creator"] has UnkownForm:
            if "created_by_email" in form_dict["creator"].cleaned_data:
                activity.created_by_email = form_dict["creator"].cleaned_data[
                    "created_by_email"
                ]
                activity.created_by_name = form_dict["creator"].cleaned_data[
                    "created_by_name"
                ]

            if self.request.user.is_authenticated:
                activity.authors.add(self.request.user)

            activity.save()

        if activity.created_by_email:
            send_mail(
                subject="Inspi: Deine Idee wurde erstellt",
                message=f"""
                    Hallo, 
                    deine neue Idee wurde erstellt. Bitte überprüfe die Idee:
                    Link: https://gruppenstunde.de/activity/detail/{activity.id}

                    Beste Grüße
                    Inspi
                """,
                recipient_list=[activity.created_by_email],
            )

        if self.request.user.is_authenticated:
            send_mail(
                subject="Inspi: Deine Idee wurde erstellt",
                message=f"""
                    Hallo, 
                    deine neue Idee wurde erstellt. Bitte überprüfe die Idee:
                    Link: https://gruppenstunde.de/activity/detail/{activity.id}

                    Beste Grüße
                    Inspi
                """,
                recipient_list=[self.request.user.email],
            )

        # red env EMAIL_HOST_USER

        send_mail(
            subject="Inspi: Eine neue Idee wurde erstellt",
            message=f"""
                Hallo, 
                eine neue Idee wurde erstellt. Bitte überprüfe die Idee:
                Link: https://gruppenstunde.de/activity/detail/{activity.id}

                Beste Grüße
                Inspi
            """,
            recipient_list=[
                user.email
                for user in CustomUser.objects.filter(
                    Q(is_superuser=True) | Q(is_staff=True)
                )
            ],
        )

        return HttpResponseRedirect(f"/activity/create-final/{activity.id}")


def create_choice(request):
    return render(request, "activity/create/start.html")


def create_final(request, pk):
    item = Activity.objects.get(pk=pk)
    context = {"activity": item}
    return render(request, "activity/create/final.html", context)


from django.http.response import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from .forms import MaterialItemForm, MaterialItemModelForm
from .models import MaterialName, MaterialItem, Activity, MaterialUnit
from django.contrib.admin.views.decorators import staff_member_required


def create_material_item(request, activity_id):
    material_items = MaterialItem.objects.filter(activity_id=activity_id)
    activity = Activity.objects.get(id=activity_id)
    form = MaterialItemForm(
        request.POST or None, initial={"quantity": 1, "material_unit": 1}
    )

    material_name_str = form.data.get("material_name")

    if not MaterialName.objects.filter(name=material_name_str).exists():
        material_name = MaterialName.objects.create(name=material_name_str)
        material_name.save()
    else:
        material_name = MaterialName.objects.get(name=material_name_str)

    if request.method == "POST":
        if form.is_valid():

            material_item = MaterialItem.objects.create(
                number_of_participants=6,
                quantity=form.data.get("quantity"),
                material_name=material_name,
                material_unit=MaterialUnit.objects.get(
                    id=form.data.get("material_unit")
                ),
                activity=activity,
            )
            return redirect("detail-material-item", pk=material_item.id)
        else:
            return render(
                request,
                "activity/partials/material-item-form.html",
                context={
                    "form": form,
                    "material_items": material_items,
                    "activity": activity,
                },
            )

    context = {"form": form, "material_items": material_items, "activity": activity}

    return render(request, "activity/create-material-item.html", context)


def update_material_item(request, pk):
    material_item = MaterialItem.objects.get(id=pk)

    if request.method == "POST":

        material_name_str = request.POST.get("material_name")

        if not MaterialName.objects.filter(name=material_name_str).exists():
            material_name = MaterialName.objects.create(name=material_name_str)
            material_name.save()
        else:
            material_name = MaterialName.objects.get(name=material_name_str)

        material_item = MaterialItem.objects.update(
            quantity=request.POST.get("quantity"),
            material_name=material_name,
            material_unit=MaterialUnit.objects.get(
                id=request.POST.get("material_unit")
            ),
            activity=Activity.objects.get(id=1),
        )

        return redirect("detail-material-item", pk=material_item)
    else:
        data = {
            "quantity": material_item.quantity,
            "material_name": material_item.material_name.name,
            "material_unit": material_item.material_unit,
        }
        form = MaterialItemForm(data)

    context = {
        "form": form,
        "material_item": material_item,
        "activity": material_item.activity,
    }

    return render(request, "activity/partials/material-item-form.html", context)


def delete_material_item(request, pk):
    material_item = get_object_or_404(MaterialItem, id=pk)

    if request.method == "POST":
        material_item.delete()
        return HttpResponse("")

    return HttpResponseNotAllowed(
        [
            "POST",
        ]
    )


def detail_material_item(request, pk):
    material_item = MaterialItem.objects.get(id=pk)
    context = {"material_item": material_item}
    return render(request, "activity/partials/material-item-detail.html", context)


def create_material_item_form(request, activity_id):
    form = MaterialItemForm(initial={"quantity": 1, "material_unit": 1})
    context = {"form": form, "activity": {"id": activity_id}}
    return render(request, "activity/partials/material-item-form.html", context)


def update_rating(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    form = RatingForm(request.POST or None, instance=activity)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    return render(
        request,
        "activity/update/rating-form.html",
        {"activity": activity, "form": form},
    )


def update_topic(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    form = TopicForm(request.POST or None, instance=activity)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    return render(
        request,
        "activity/update/topics-form.html",
        {"activity": activity, "form": form},
    )


def update_choices(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    form = ChoicesForm(request.POST or None, instance=activity)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    return render(
        request,
        "activity/update/choices-form.html",
        {"activity": activity, "form": form},
    )


def update_material(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    material_items = MaterialItem.objects.filter(activity_id=activity_id)
    form = MaterialItemForm(request.POST or None)

    material_name_str = form.data.get("material_name", "")

    if (
        not MaterialName.objects.filter(name=material_name_str).exists()
        and not material_name_str == ""
    ):
        material_name = MaterialName.objects.create(name=material_name_str)
        material_name.save()
    else:
        material_name = MaterialName.objects.get(name=material_name_str)

    if request.method == "POST":
        if form.is_valid():

            material_item = MaterialItem.objects.create(
                number_of_participants=6,
                quantity=form.data.get("quantity"),
                material_name=material_name,
                material_unit=form.data.get("material_unit"),
                activity=activity,
            )
            return redirect("detail-material-item", pk=material_item.id)
        else:
            return render(
                request,
                "activity/partials/material-item-form.html",
                context={"form": form, "activity": activity},
            )

    context = {"form": form, "material_items": material_items, "activity": activity}

    return render(request, "activity/create-material-item.html", context)


def update_header_text(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    form = HeaderTextForm(request.POST or None, instance=activity)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    return render(
        request,
        "activity/update/header-text-form.html",
        {"activity": activity, "form": form},
    )


def update_creator(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    form = CreatorForm(request.POST or None, instance=activity)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    return render(
        request,
        "activity/update/creator-form.html",
        {"activity": activity, "form": form},
    )


def update_image(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES, instance=activity)
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    form = ImageForm(instance=activity)
    return render(
        request, "activity/update/image-form.html", {"activity": activity, "form": form}
    )


def update_crop(request, activity_id):
    activity = Activity.objects.get(id=activity_id)

    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES, instance=activity)
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    form = ImageForm(instance=activity)
    return render(
        request, "activity/update/image-form.html", {"activity": activity, "form": form}
    )


def activity_archive(request, activity_id):
    me = request.user
    item = Activity.objects.get(id=activity_id)
    if not item.is_allowed_to_edit(me):
        messages.error(request, "You are not allowed to archive this activity")
        # activity-list
        return redirect("activity-list")
    item.status = activity_choices.StatusSearchChoices.ARCHIVED
    item.save()
    messages.warning(request, "Idee archiviert")
    return redirect("activity-list")


def activity_publish(request, activity_id):
    me = request.user
    item = Activity.objects.get(id=activity_id)
    if not item.is_allowed_to_edit(me):
        messages.error(request, "You are not allowed to publish this post")
        return redirect("activity-list")
    item.status = activity_choices.StatusSearchChoices.PUBLISHED
    item.save()
    messages.success(request, "Idee veröffentlicht")
    return redirect("activity-list")


def update_main_text(request, activity_id):
    activity = Activity.objects.get(id=activity_id)
    form = MainTextForm(request.POST or None, instance=activity)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("activity-detail", activity_id=activity_id)

    return render(
        request,
        "activity/update/main-text-form.html",
        {"activity": activity, "form": form},
    )


def comment_create(request):
    data = json.loads(request.body)
    activity_id = data["activity_id"]
    content = data["content"]

    activity = get_object_or_404(Activity, id=activity_id)
    comment = activity_models.Comment.objects.create(
        author=request.user, content=content, activity=activity
    )

    return JsonResponse(
        {
            "author": comment.author.username,
            "content": comment.content,
            "timestamp": date_format(comment.date_posted, "SHORT_DATETIME_FORMAT"),
        }
    )


link_list = [
    {
        "link": "activity-admin-overview",
        "title": "Übersicht",
    },
    {
        "link": "activity-admin-event-of-week",
        "title": "Idee der Woche",
    },
    {
        "link": "activity-admin-like",
        "title": "Likes",
    },
    {
        "link": "activity-admin-topic",
        "title": "Themen",
    },
    {
        "link": "activity-admin-user-behavior",
        "title": "Nutzerdaten",
    },
    {
        "link": "activity-admin-comment",
        "title": "Kommentare",
    },
    {
        "link": "activity-ai-overview",
        "title": "AI Improvements",
    },
]


def admin_overview(request):
    context = {"link_list": link_list}
    return render(request, "activity/admin/overview/main.html", context)


def admin_event_of_week(request):
    context = {
        "id": "event-of-week",
        "link_list": link_list,
        "form": StatusSearchFrom(request.GET or None),
        "items": activity_models.ActivityOfTheWeek.objects.all().order_by(
            "-release_date"
        ),
        "create_link": "event-of-week/create",
        "update_link": "event-of-week/update",
    }
    return render(request, "activity/admin/activity-of-week/main.html", context)


def admin_topic(request):
    context = {
        "id": "topic",
        "link_list": link_list,
        "items": activity_models.Topic.objects.all().order_by("sorting"),
        "update_link": "topic/update",
        "create_link": "topic/create",
    }
    return render(request, "activity/admin/comment/main.html", context)


def admin_comment(request):
    context = {
        "id": "comment",
        "link_list": link_list,
        "items": activity_models.Comment.objects.all(),
        "update_link": "comment/update",
    }
    return render(request, "activity/admin/comment/main.html", context)


def admin_data(request):
    visitors = Visitor.objects.filter(
        Q(start_time__gte=timezone.now() - timezone.timedelta(days=14))
        and Q(time_on_site__gte=1)
    )

    visitors_per_day = (
        visitors.annotate(day=TruncDay("start_time"))
        .values("day")
        .annotate(total=Count("session_key"))
        .order_by("day")
    )

    visitors_per_day = {
        visitor["day"].strftime("%Y-%m-%d"): visitor["total"]
        for visitor in visitors_per_day
    }

    visitors_last_7_days = (
        visitors.filter(
            start_time__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
    )

    vistor_trend = (
        round(
            (4 * visitors_last_7_days[0])
            / (
                visitors.filter(
                    Q(start_time__gte=timezone.now() - timezone.timedelta(days=28))
                    and Q(start_time__lt=timezone.now() - timezone.timedelta(days=7))
                ).count()
                + 1
            ),
            1,
        ),
    )

    context = {
        "link_list": link_list,
        "visitors_per_day": visitors_per_day,
        "visitors_last_7_days": visitors_last_7_days[0],
        "vistor_trend": vistor_trend[0],
    }

    return render(request, "activity/admin/user-behavior/main.html", context)


def admin_like(request):
    context = {
        "id": "comment",
        "link_list": link_list,
        "items": activity_models.Emotion.objects.all(),
        "update_link": "emotion/update",
    }
    return render(request, "activity/admin/comment/main.html", context)


def event_of_week_create(request):
    if request.method == "POST":
        form = EventOfWeekForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("activity-admin-event-of-week")
    else:
        form = EventOfWeekForm()
    context = {"form": form}
    return render(request, "activity/admin/components/list/create.html", context)


def event_of_week_update(request, id):
    item = activity_models.ActivityOfTheWeek.objects.get(id=id)

    if request.method == "POST":
        form = EventOfWeekForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("activity-admin-event-of-week")
    else:
        form = EventOfWeekForm(instance=item)
    context = {"form": form}
    return render(request, "activity/admin/components/list/update.html", context)


def comment_update(request, id):
    item = activity_models.Comment.objects.get(id=id)

    if request.method == "POST":
        form = CommentAdminForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("activity-admin-comment")
    else:
        form = CommentAdminForm(instance=item)
    context = {"form": form}
    return render(request, "activity/admin/components/list/update.html", context)


def emotion_update(request, id):
    item = activity_models.Emotion.objects.get(id=id)

    if request.method == "POST":
        form = EmotionAdminForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect("activity-admin-like")
    else:
        form = EmotionAdminForm(instance=item)
    context = {"form": form}
    return render(request, "activity/admin/components/list/update.html", context)

def add_emotion(request):
    activity_id = request.POST.get("activity_id")
    emotion = request.POST.get("emotion")

    activity = get_object_or_404(Activity, id=activity_id)

    if request.user.is_authenticated:
        activity_models.Emotion.objects.create(
            activity=activity,
            emotion=emotion,
            created_by=request.user,
            created_at=timezone.now(),
        )

        return JsonResponse("Danke!", safe=False)
    else:
        activity_models.Emotion.objects.create(
            activity=activity,
            emotion=emotion,
            created_at=timezone.now(),
        )
        # render html
        return JsonResponse("Danke!", safe=False)

@staff_member_required
def topic_create(request):
    if request.method == "POST":
        form = TopicAdminForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("activity-admin-topic")
    else:
        form = TopicAdminForm()
    context = {"form": form}
    return render(request, "activity/admin/components/list/create.html", context)

@staff_member_required
def topic_update(request, id):
    item = activity_models.Topic.objects.get(id=id)

    if request.method == "POST":
        form = TopicAdminForm(request.POST, instance=item)
        if form.is_valid():
            return redirect("activity-admin-topic")
    else:
        form = TopicAdminForm(instance=item)
    context = {"form": form}
    return render(request, "activity/admin/components/list/update.html", context)


@staff_member_required
def admin_ai(request):
    if request.method == "POST":
        form = AiForm(request.POST)
        if form.is_valid():
            activity = form.cleaned_data["activity"]
            promtType = form.cleaned_data["promtType"]
            model = form.cleaned_data["model"]

            activity_id = activity.id

            activity = activity_models.Activity.objects.get(id=activity_id)

            text_old = ""
            text_type = 'text'

            if promtType == "description":
                promt = f"""
                    Verbessere und verschönere den folgenden Text, in deutscher Sprache.
                    Der Output muss HTML Code sein.
                    Der HTML Code soll für Jugendliche sein: Der Text soll für Jugendliche
                    sein: Inhalt: {activity.description} der Titel ist {activity.title} und die
                    Zusammenfassung ist {activity.summary} und viele Absätze enthalten, html Listen <ul> und aufzählungen.
                    dazu soll der Text ansprechend formatiert sein z.B. mit <b> <k> etc.
                    Es dürfen auch weitere Beispiele oder Varainaten hinzu gefügt werden.
                    Aber die Schriftgröße soll nicht verändert werden, dazu soll keine Farbe drinnen sein.
                """
                text_old = activity.description
                text_type = 'html'
                class OutputModel(BaseModel):
                    text: str = Field(min_length=100, max_length=10000)
            elif promtType == "summary":
                promt = f"""
                    Fasse den folgenden Text, in deutscher Sprache,
                    in 100 Zeichen als werbenden Aussagesatz zusammen.
                    Der Text soll für Jugendliche sein: Inhalt: {activity.description} der Titel ist {activity.title} und die Zusammenfassung ist {activity.summary}
                """
                text_old = activity.summary
                class OutputModel(BaseModel):
                    text: str = Field(min_length=80, max_length=120)
            elif promtType == "summary_long":
                promt = f"""
                    Fasse den folgenden Text, in deutscher Sprache,
                    in 1000 Zeichen als interante Text zusammen.
                    Der Text soll für Jugendliche sein: Inhalt: {activity.description} der Titel ist {activity.title} und die Zusammenfassung ist {activity.summary}
                """
                text_old = activity.summary_long
                class OutputModel(BaseModel):
                    text: str = Field(min_length=800, max_length=1200)
            elif promtType == "title":
                promt = f"""
                    Fasse den folgenden Text, in deutscher Sprache,
                    in maximal 20 Zeichen als aussagekräftigen Titel zusammen.
                    Der Text soll für Jugendliche sein: Inhalt: {activity.description} der Titel ist {activity.title} und die Zusammenfassung ist {activity.summary}
                """
                text_old = activity.title
                class OutputModel(BaseModel):
                    text: str = Field(min_length=10, max_length=20)
            else:
                "werfe einen Fehler"

            context = {
                "text_suggestion": get_ai_suggestion(prompt=promt, model=model, OutputModel=OutputModel),
                "text_old": text_old,
                "promtType" : promtType,
                "text_type": text_type,
                "title": activity.title,
                "activity_id": activity.id,
            }

            return render(request, "activity/admin/ai/suggestion.html", context)
    form = AiForm(
        initial={
            "model": "models/gemini-1.5-flash-latest"
        }
    )
    context = {
        "form": form,
        "link_list": link_list,
    }
    return render(request, "activity/admin/ai/main.html", context)
