import json
from django.shortcuts import render


from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.forms.models import inlineformset_factory
from formtools.wizard.views import SessionWizardView, CookieWizardView
from django.db.models import Q

from django.shortcuts import get_object_or_404
from django.utils.formats import date_format

from django.contrib import messages

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
        selected_scout_level = activity_models.ScoutLevelChoice.objects.get(id=scout_level_id)
    else:
        selected_scout_level = None
    
    topics = activity_models.Topic.objects.all()

    activities_raw = activities_raw.filter(
        status=activity_choices.StatusSearchChoices.PUBLISHED
    )

    newest_activities = activities_raw.order_by("-created_at")[:4]
    famous_activities = activities_raw.order_by("-view_count")[:4]
    random_activities = activities_raw.order_by("?")[:4]

    context = {
        "newest_activities": newest_activities,
        "famous_activities": famous_activities,
        "random_activities": random_activities,
        "topics": topics,
        "selected_topic": selected_topic,
        "selected_scout_level": selected_scout_level,

    }
    return render(request, "activity/main-view.html", context)


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


def admin_main(request):
    return render(request, "activity/admin/main.html")
