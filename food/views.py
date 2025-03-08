from django_filters import CharFilter, NumberFilter
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from pydantic import Field, BaseModel, PositiveFloat

from django.contrib import messages


from copy import deepcopy

from general.login.models import CustomUser
from activity.activity.service.admin.ai_suggestion import get_ai_suggestion
import random
from enum import Enum
from typing import List

from .forms import (
    MealEventForm,
    SearchForm,
    MealEventTemplateFormCreate,
    MealEventTemplateFormUpdate,
    IngredientForm,
    IngredientFormCopy,
    IngredientFormAi,
    PortionFormCreate,
    PortionFormUpdate,
    PriceForm,
    PriceFormUpdate,
    IngredientFormUpdateBasic,
    IngredientFormUpdateAttribute,
    IngredientFormUpdateRef,
    IngredientFormUpdateNutrition,
    RecipeItemFormCreate,
    RecipeItemFormUpdate,
    RecipeFormUpdate,
    MealForm,
    MealDayForm,
    MealItemFormCreate,
    MealItemFormUpdate,
    SearchRecipeForm,
    SearchPlanForm,
)
from .models import (
    MealEvent,
    Recipe,
    Ingredient,
    MealEventTemplate,
    Portion,
    Price,
    MetaInfo,
    RecipeItem,
    MeasuringUnit,
    MealDay,
    Meal,
    MealItem,
    RetailSection,
    Intolerance,
    TemplateOption,
)

# import update_recipe from service
from .service.recipe import update_recipe
from .service.nutri_lib import get_nutri_items, update_meta_info_nutri


# create view with template main.html


@login_required
def mainView(request):
    famous_meal_events = MealEvent.objects.all()[0:3]
    famous_recipes = Recipe.objects.filter(~Q(status="simulator"))[0:3]
    famous_ingredients = Ingredient.objects.all()[0:8]

    context = {
        "famous_meal_events": famous_meal_events,
        "famous_recipes": famous_recipes,
        "famous_ingredients": famous_ingredients,
    }
    return render(request, "main.html", context)


@login_required
def food_dashboard(request):
    kpi_own_meal_events = MealEvent.objects.filter(managed_by=request.user).count()
    kpi_all_meal_events = MealEvent.objects.all().count()
    kpi_all_recipes = Recipe.objects.filter(~Q(status="simulator")).count()
    kpi_all_ingredients = Ingredient.objects.all().count()

    context = {
        "kpi_own_meal_events": kpi_own_meal_events,
        "kpi_all_meal_events": kpi_all_meal_events,
        "kpi_all_recipes": kpi_all_recipes,
        "kpi_all_ingredients": kpi_all_ingredients,
    }
    return render(request, "food-dashboard/main.html", context)


@login_required
def plan(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Übersicht",
    }
    return render(request, "plan/time-table/plan.html", context)


@login_required
def plan_detail_overview(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    # event_name
    plan_list = [
        {"title": "Name", "value": plan.event_name},
        {"title": "Beschreibung", "value": plan.description},
        # norm_portions
        {"title": "Aktuelle Normportionen", "value": plan.norm_portions},
        # activity_factor
        {"title": "Aktivitätsfaktor", "value": plan.get_activity_factor_display},
        # reserve_factor
        {"title": "Reservefaktor", "value": plan.reserve_factor},
        # is_public
        {"title": "Öffentlich?", "value": plan.is_public},
        # is_approved
        {"title": "Von Inspi Überprüft", "value": plan.is_approved},
        # managed_by
        {
            "title": "Verantwortlich",
            "value": (
                ", ".join(user.username for user in plan.managed_by.all())
                if plan.managed_by.exists()
                else "kein Verantwortlicher"
            ),
        },
        # day_count
        {"title": "Tage", "value": f"{len(plan.list_meal_days())} Tage"},
        # list meal count
        {"title": "Mahlzeiten", "value": f"{len(plan.list_meals())} Mahlzeiten"},
    ]

    template_list = [
        {"title": "Vorlagen Name", "value": plan.meal_event_template.name},
        {"title": "Beschreibung", "value": plan.meal_event_template.description},
        {"title": "Öffentlich", "value": plan.meal_event_template.is_public},
        {
            "title": "Maximaler Preis",
            "value": f"{plan.meal_event_template.max_price_eur} €",
        },
        {
            "title": "Geeignet für",
            "value": plan.meal_event_template.get_suit_level_display,
        },
        {
            "title": "Warmes Essen",
            "value": plan.meal_event_template.get_warm_meal_display,
        },
        {
            "title": "Essenszeit Optionen",
            "value": plan.meal_event_template.get_meal_time_options_display,
        },
        {
            "title": "Kinderfreundlich",
            "value": plan.meal_event_template.get_child_frendly_display,
        },
        {
            "title": "Unverträglichkeiten",
            "value": (
                ", ".join(
                    [
                        intolerance.name
                        for intolerance in plan.meal_event_template.intolerances.all()
                    ]
                )
                if plan.meal_event_template.intolerances.exists()
                else "keine Einschränkungen"
            ),
        },
    ]

    meta_info_list = [
        {"title": "Nutri Klasse", "value": plan.meta_info.nutri_class},
        # price_eur
        {"title": "Preis", "value": plan.meta_info.price_eur},
    ]

    context = {
        "plan": plan,
        "module_name": "Übersicht",
        "plan_list": plan_list,
        "template_list": template_list,
        "meta_info_list": meta_info_list,
    }
    return render(request, "plan/detail/overview/main.html", context)


@login_required
def plan_detail_participant(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Teilnehmer",
    }
    return render(request, "plan/detail/participant/main.html", context)


@login_required
def plan_detail_plan_editor(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Editor",
    }
    return render(request, "plan/detail/plan-editor/main.html", context)


@login_required
def plan_detail_shopping_list(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Einkaufsliste",
    }
    return render(request, "plan/detail/shopping-list/main.html", context)


@login_required
def plan_detail_time_table(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Zeitplan",
    }
    return render(request, "plan/detail/time-table/main.html", context)


@login_required
def plan_editor(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Editor",
    }
    return render(request, "plan/editor/plan-editor.html", context)


@login_required
def plan_create(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = MealEventForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            data["slug"] = data["title"].replace(" ", "-").lower()

            # remove categories from data
            categories = data.pop("categories")

            # create a new post
            plan = MealEvent(**data)
            plan.author = CustomUser.objects.first()
            plan.save()
            for category in categories:
                plan.categories.add(category)

            return HttpResponseRedirect("/food/plan-list/")

        return render(request, "plan/create/plan-create.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MealEventForm()
        return render(request, "plan/create/plan-create.html", {"form": form})


@login_required
def plan_dashboard(request):
    plans = MealEvent.objects.all()
    form = SearchPlanForm(request.GET)

    paginator = Paginator(plans, per_page=10)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "page_obj": page_obj,
        "form": form,
    }
    return render(request, "plan/list/main.html", context)


@login_required
def template_create(request):
    if request.method == "POST":
        form = MealEventTemplateFormCreate(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            intolerances = data.pop("intolerances")
            template_options = data.pop("template_options")

            template = MealEventTemplate(**data)

            template.created_by = CustomUser.objects.first()
            template.created_at = timezone.now()
            template.save()

            for intolerance in intolerances:
                try:
                    intolerance_obj = Intolerance.objects.get(name=intolerance)
                    template.intolerances.add(intolerance_obj)
                except Intolerance.DoesNotExist:
                    # Handle the case where the intolerance does not exist
                    print(f"Intolerance '{intolerance}' does not exist.")

            for template_option in template_options:
                try:
                    template_option_obj = TemplateOption.objects.get(
                        name=template_option
                    )
                    template.template_options.add(template_option_obj)
                except TemplateOption.DoesNotExist:
                    # Handle the case where the template option does not exist
                    print(f"Template option '{template_option}' does not exist.")

            event_name = f"{template.name}-{str(random.randint(1, 10000))}"
            event_name_slug = event_name.replace(" ", "-").lower()
            # create meal events from template
            new_meal_event = MealEvent.objects.create(
                # add random number to name
                event_name=event_name,
                slug=event_name_slug,
                description=template.description,
                meal_event_template=template,
                norm_portions=1,
                reserve_factor=1.0,
                activity_factor="Z",
                is_public=template.is_public,
                is_approved=False,
            )
            # add meta info
            new_meta_info = MetaInfo.objects.create()
            new_meal_event.meta_info = new_meta_info
            new_meal_event.save()

            # add three meal_day
            for i in range(1, 4):
                new_meal_day = MealDay.objects.create(
                    meal_event=new_meal_event,
                    max_day_part_factor=1.0,
                )
                # add meta info
                new_meta_info = MetaInfo.objects.create()
                new_meal_day.meta_info = new_meta_info
                new_meal_day.save()

                meal_types = [
                    {
                        "name": "Tagesgetränke",
                        "meal_type": "drinks",
                        "day_part_factor": 1.0,
                    },
                    {
                        "name": "Tages-Snacks",
                        "meal_type": "snacks",
                        "day_part_factor": 1.0,
                    },
                    {
                        "name": "Frühstück",
                        "meal_type": "breakfast",
                        "day_part_factor": 1.0,
                        "time_start": "07:00",
                        "time_end": "08:00",
                    },
                    {
                        "name": "Mittagessen",
                        "meal_type": "lunch",
                        "day_part_factor": 1.0,
                        "time_start": "12:00",
                        "time_end": "13:00",
                    },
                    {
                        "name": "Abendessen",
                        "meal_type": "dinner",
                        "day_part_factor": 1.0,
                        "time_start": "18:00",
                        "time_end": "19:00",
                    },
                    {
                        "name": "Abend-Snacks",
                        "meal_type": "evening_snacks",
                        "day_part_factor": 1.0,
                        "time_start": "21:00",
                        "time_end": "22:00",
                    },
                ]
                for meal_type in meal_types:
                    new_meal = Meal.objects.create(
                        meal_day=new_meal_day,
                        name=meal_type["name"],
                        meal_type=meal_type["meal_type"],
                        day_part_factor=meal_type["day_part_factor"],
                        time_start=meal_type.get("time_start", None),
                        time_end=meal_type.get("time_end", None),
                    )
                    # add meta info
                    new_meta_info = MetaInfo.objects.create()
                    new_meal.meta_info = new_meta_info
                    new_meal.save()

                    # add a random recipe
                    recipes = Recipe.objects.all()
                    random_recipe = recipes[random.randint(0, len(recipes) - 1)]

                    new_meal_item = MealItem.objects.create(
                        meal=new_meal,
                        recipe=random_recipe,
                        factor=1.0,
                    )

                    # add meta info
                    new_meta_info = MetaInfo.objects.create()
                    new_meal_item.meta_info = new_meta_info

                    new_meal_item.save()

            return HttpResponseRedirect(f"/food/plan/{event_name_slug}/overview")

    form = MealEventTemplateFormCreate(
        initial={
            "name": "Neue Veranstaltung",
            "description": "",
            "max_price_eur": 7.00,
            "suit_level": "M",
            "warm_meal": "J",
            "meal_time_options": "SW",
            "child_frendly": "CA",
        }
    )
    return render(request, "plan/plan-template/create.html", {"form": form})


@login_required
def template_update(request, id):
    instance = get_object_or_404(MealEventTemplate, id=id)
    meal_event = MealEvent.objects.get(meal_event_template=instance)
    if request.method == "POST":
        form = MealEventTemplateFormUpdate(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/plan/{meal_event.slug}/overview")
    form = MealEventTemplateFormUpdate(instance=instance)

    context = {
        "template": instance,
        "form": form,
        "plan": meal_event,
    }
    return render(request, "plan/plan-template/update.html", context)


def meal_detail_overview(request, slug, id):
    meal = Meal.objects.get(id=id)
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "meal": meal,
        "plan": plan,
        "module_name": "Übersicht",
        "recipes": Recipe.objects.all(),
        "create_form": MealItemFormCreate(
            initial={"meal": meal, "factor": 1.0, "recipe": Recipe.objects.first()}
        ),
    }
    return render(request, "meal/detail/overview/main.html", context)


@login_required
def meal_event_create(request):
    templates = MealEventTemplate.objects.all()
    context = {
        "templates": templates,
    }
    return render(request, "plan/create/meal-event-create.html", context)


@login_required
def meal_event_clone(request):
    mealEvents = MealEvent.objects.all()
    context = {
        "mealEvents": mealEvents,
    }
    return render(request, "plan/create/meal-event-clone.html", context)


def meal_event_update(request, id):
    instance = get_object_or_404(MealEvent, id=id)
    if request.method == "POST":
        form = MealEventForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/plan/{instance.slug}/overview")
    form = MealEventForm(instance=instance)

    context = {
        "plan": instance,
        "form": form,
    }
    return render(request, "meal-event-update.html", context)


def meal_event_delete(request):
    if request.method == "POST":
        meal_event_id = request.POST.get("meal_event_id")
        meal_event = MealEvent.objects.get(pk=meal_event_id)
        meal_event.delete()

    return HttpResponse("")


def meal_create(request, meal_day_id):
    if request.method == "POST":
        form = MealForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            # create a new post
            meal = Meal(**data)
            meal.author = CustomUser.objects.first()
            meal.save()

            meal_day_id = MealDay.objects.get(pk=meal_day_id)

            return HttpResponseRedirect(
                f"/food/plan/{meal_day_id.meal_event.slug}/overview"
            )

        return render(request, "meal/create/main.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        meal_day = MealDay.objects.get(pk=meal_day_id)
        form = MealForm(initial={"meal_day": meal_day})
        return render(request, "meal/create/main.html", {"form": form})


def meal_update(request, id):
    instance = get_object_or_404(Meal, id=id)
    if request.method == "POST":
        form = MealForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/plan/{instance.slug}/overview")
    form = MealForm(instance=instance)

    context = {
        "meal": instance,
        "form": form,
    }
    return render(request, "meal-update.html", context)


def meal_delete(request, id):
    instance = get_object_or_404(Meal, id=id)
    instance.delete()

    return HttpResponse("")


@login_required
def meal_item_create(request):
    if request.method == "POST":
        meal = Meal.objects.get(pk=request.POST.get("meal"))
        recipe = Recipe.objects.get(pk=request.POST.get("recipe"))
        form = MealItemFormCreate(
            data={
                "meal": meal,
                "factor": request.POST.get("factor"),
                "recipe": recipe,
            }
        )

        if form.is_valid():
            data = form.cleaned_data

            # create a new post
            meal_item = MealItem(**data)
            meal_item.created_by = request.user
            # add meta info
            new_meta_info = MetaInfo.objects.create(
                weight_g=meal_item.recipe.meta_info.weight_g * meal_item.factor,
                price_per_kg=meal_item.recipe.meta_info.price_per_kg * meal_item.factor,
                price_eur=meal_item.recipe.meta_info.price_eur * meal_item.factor,
            )
            meal_item.meta_info = new_meta_info
            meal_item.save()

            return HttpResponseRedirect(
                f"/food/plan/{meal.meal_day.meal_event.slug}/meal/{meal.id}/overview"
            )


@login_required
def meal_item_update(request, slug):
    instance = get_object_or_404(MealItem, id=id)
    if request.method == "POST":
        form = MealItemFormUpdate(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/dashboard/")
    form = MealItemFormUpdate(instance=instance)

    context = {
        "meal_item": instance,
        "form": form,
    }
    return render(request, "meal-item/update.html", context)


def meal_day_update(request, id):
    instance = get_object_or_404(MealDay, id=id)
    plan = instance.meal_event
    if request.method == "POST":
        form = MealDayForm(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/plan/{plan.slug}")
    form = MealDayForm(instance=instance)

    context = {
        "meal_day": instance,
        "form": form,
    }
    return render(request, "meal/meal-day/update.html", context)


def meal_day_delete(request, id):
    instance = get_object_or_404(MealDay, id=id)
    event = instance.meal_event
    instance.delete()

    # success response 200
    return HttpResponse("")


@login_required
def plan_shopping_cart(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    shopping_list = []

    for meal in plan.list_meals():
        for meal_item in meal.list_meal_items():
            for recipe_item in meal_item.recipe.recipe_items.all():
                shopping_list.append(
                    {
                        "ingredient": recipe_item.portion.ingredient.name,
                        "retail_section": recipe_item.portion.ingredient.retail_section,
                        "recipe_name": recipe_item.recipe.name,
                        "quantity": recipe_item.quantity * meal_item.factor,
                        "weight_g": recipe_item.meta_info.weight_g,
                        "price": recipe_item.portion.meta_info.price_per_kg
                        * (recipe_item.portion.meta_info.weight_g / 1000)
                        * recipe_item.quantity
                        * meal_item.factor,
                    }
                )

    # sum up the shopping list by ingredient
    shopping_list = [
        {
            "ingredient": item["ingredient"],
            "quantity": sum(
                [
                    i["quantity"]
                    for i in shopping_list
                    if i["ingredient"] == item["ingredient"]
                ]
            ),
            "retail_section": item["retail_section"],
            "recipe_name": ", ".join(
                set(
                    [
                        i["recipe_name"]
                        for i in shopping_list
                        if i["ingredient"] == item["ingredient"]
                    ]
                )
            ),
            "weight_g": item["weight_g"],
            "price": sum(
                [
                    i["price"]
                    for i in shopping_list
                    if i["ingredient"] == item["ingredient"]
                ]
            ),
        }
        for item in shopping_list
    ]

    # deduplicate the shopping list
    shopping_list = [dict(t) for t in {tuple(d.items()) for d in shopping_list}]

    # sort by retail_section
    shopping_list = sorted(shopping_list, key=lambda x: str(x["retail_section"]) or "")

    context = {
        "plan": plan,
        "shopping_list": shopping_list,
        "module_name": "Einkaufsliste",
        "total_price": sum([item["price"] for item in shopping_list]),
        "total_weight": sum(
            [item["quantity"] * item["weight_g"] for item in shopping_list]
        )
        * 0.001
        * 0.001,
    }
    return render(request, "plan/shopping-list/shopping-list.html", context)


@login_required
def plan_participants(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    context = {"plan": plan, "module_name": "Teilnehmer"}
    return render(request, "plan/participant/participants.html", context)


@login_required
def ingredient_create_choice(request):
    boxes = [
        {
            "header": "Komplett selbst",
            "text": """
                Mit dieser Option kannst du ein neues Lebensmittel komplett selbst erstellen und jedes Detail selbst bestimmen.
                Eine Anlage dauert allerdings ein paar Minuten.
            """,
            "link": "ingredient-create",
            "icon": "adjust",
        },
        {
            "header": "Auf Basis eines anderen Lebensmittels",
            "text": """
                Mit dieser Option kannst du ein neues Lebensmittel auf Basis eines anderen Lebensmittels erstellen.
                Nutze diese Option wenn du ein Lebensmittel erstellen möchtest, dass sich nur in wenigen Details von
                einem bereits existierenden Lebensmittel unterscheidet. z.B. Cocktail- und Rispentomate.
            """,
            "link": "ingredient-create-copy",
            "icon": "copy",
        },
        {
            "header": "Mit Hilfe eines KI Vorschlags",
            "text": """
                Mit dieser Option kannst du ein neues Lebensmittel auf Basis eines KI Vorschlags erstellen.
                Alle Daten werden von einer Sprach KI generiert und können dann von dir noch angepasst werden.
            """,
            "link": "ingredient-create-ai",
            "icon": "brain",
        },
    ]
    context = {
        "boxes": boxes,
    }
    return render(request, "ingredient/create/choice/main.html", context)


@login_required
def ingredient_create(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:

        form = IngredientForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            data["slug"] = data["name"].replace(" ", "-").lower()

            # remove portions, unprepared_eatable, intolerances from data
            portions = data.pop("portions")
            unprepared_eatable = data.pop("unprepared_eatable")
            intolerances = data.pop("intolerances")

            energy_kj = data.pop("energy_kj", 0)
            protein_g = data.pop("protein_g", 0)
            fat_g = data.pop("fat_g", 0)
            fat_sat_g = data.pop("fat_sat_g", 0)
            sugar_g = data.pop("sugar_g", 0)
            salt_g = data.pop("salt_g", 0)
            fruit_factor = data.pop("fruit_factor", 0)
            carbohydrate_g = data.pop("carbohydrate_g", 0)
            fibre_g = data.pop("fibre_g", 0)

            # create a new post
            ingredient = Ingredient(**data)
            ingredient.author = CustomUser.objects.first()
            # add meta info
            new_meta_info = MetaInfo.objects.create()
            ingredient.meta_info = new_meta_info

            ingredient.save()

            new_portion_meta_info = MetaInfo.objects.create(
                weight_g=1.0,
            )
            new_portion = Portion.objects.create(
                name=f"{ingredient.name} in g",
                ingredient=ingredient,
                measuring_unit=MeasuringUnit.objects.get(name="g"),
                quantity=1,
                meta_info=new_portion_meta_info,
            )

            ingredient.portions.add(new_portion)

            return HttpResponseRedirect("/food/ingredient-list/")

    form = IngredientForm()
    return render(
        request,
        "general/_generic_form.html",
        {"form": form, "header": "Lebensmittel erstellen"},
    )


@login_required
def ingredient_create_copy(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:

        form = IngredientFormCopy(request.POST)

        if form.is_valid():

            data_input = form.cleaned_data

            source_data = Ingredient.objects.get(id=data_input["ingredient_ref"].id)
            # deepcopy data
            data = deepcopy(source_data.__dict__)

            # remove id, created_at, updated_at, author
            data.pop("id")
            data.pop("created_at")
            data.pop("updated_at")

            # overwrite name, slug, description
            data["name"] = data_input["name"]
            data["slug"] = data_input["name"].replace(" ", "-").lower()

            # check for slug uniqueness and add a random number incase of duplicate
            if Ingredient.objects.filter(slug=data["slug"]).exists():
                data["slug"] = f"{data['slug']}-{random.randint(1, 100)}"
            data["description"] = data_input["description"]
            data["ingredient_ref"] = source_data

            valid_fields = {field.name for field in Ingredient._meta.get_fields()}
            filtered_data = {
                key: value for key, value in data.items() if key in valid_fields
            }
            ingredient = Ingredient(**filtered_data)

            ingredient.author = request.user
            # add meta info from source_data as copy
            new_meta_info = MetaInfo.objects.get(id=source_data.meta_info.id)
            # validate that the meta_info is not the same
            new_meta_info.id = None
            new_meta_info.save()
            ingredient.meta_info = new_meta_info

            ingredient.save()

            # copy portions and prices from source_data and add to ingredient
            for portion in source_data.portions.all():
                new_portion = Portion.objects.create(
                    name=portion.name,
                    ingredient=ingredient,
                    measuring_unit=portion.measuring_unit,
                    quantity=portion.quantity,
                    meta_info=portion.meta_info,
                )
                new_portion.save()

                for price in portion.prices.all():
                    new_price = Price.objects.create(
                        price_eur=price.price_eur,
                        name=price.name,
                        portion=new_portion,
                        quantity=price.quantity,
                        retailer=price.retailer,
                        quality=price.quality,
                    )
                    new_price.save()

            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/overview")

    form = IngredientFormCopy()
    return render(
        request,
        "general/_generic_form.html",
        {"form": form, "header": "Lebensmittel erstellen mit Vorlage"},
    )


@login_required
def ingredient_create_ai(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:

        form = IngredientFormAi(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            data["slug"] = data["name"].replace(" ", "-").lower()

            # create a new post
            ingredient = Ingredient(**data)
            ingredient.author = request.user
            # add meta info
            new_meta_info = MetaInfo.objects.create()
            ingredient.meta_info = new_meta_info

            ingredient.save()

            new_portion_meta_info = MetaInfo.objects.create(
                weight_g=1.0,
            )
            new_portion = Portion.objects.create(
                name=f"{ingredient.name} in g",
                ingredient=ingredient,
                measuring_unit=MeasuringUnit.objects.get(name="g"),
                quantity=1,
                meta_info=new_portion_meta_info,
            )

            ingredient.portions.add(new_portion)

            return HttpResponseRedirect("/food/ingredient-list/")

    form = IngredientFormAi()
    return render(
        request,
        "general/_generic_form.html",
        {"form": form, "header": "Lebensmittel mit KI erstellen"},
    )


@login_required
def ingredients_autocomplete(request):
    if request.method == "GET":
        query = request.GET.get("query", "")
        ingredients = Ingredient.objects.filter(name__icontains=query)[:50]
        results = [
            {"id": ingredient.id, "name": ingredient.name} for ingredient in ingredients
        ]
        return render(request, "ingredient/autocomplete.html", {"results": results})
    return


@login_required
def ingredient_update_basic(request, slug):
    # get ?next=/some/url/ from request
    name = request.GET.get("name", None)
    description = request.GET.get("description", None)
    retail_section = request.GET.get("retail_section", None)
    status = request.GET.get("status", None)

    ingredient = get_object_or_404(Ingredient, slug=slug)

    if name:
        ingredient.name = name

    if description:
        ingredient.description = description

    if retail_section:
        ingredient.retail_section = RetailSection.objects.get(name=retail_section)

    if status:
        ingredient.status = status

    if request.method == "POST":
        form = IngredientFormUpdateBasic(request.POST, instance=ingredient)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/overview")
    form = IngredientFormUpdateBasic(instance=ingredient)

    context = {
        "ingredient": ingredient,
        "form": form,
        "url_variable": "ingredient-suggestions-basic",
    }
    return render(request, "ingredient/update.html", context)


@login_required
def ingredient_update_attribute(request, slug):
    ingredient = get_object_or_404(Ingredient, slug=slug)
    intolerances = request.GET.get("intolerances", None)
    physical_viscosity = request.GET.get("physical_viscosity", None)
    physical_density = request.GET.get("physical_density", None)
    child_frendly_score = request.GET.get("child_frendly_score", None)
    scout_frendly_score = request.GET.get("scout_frendly_score", None)

    if intolerances and intolerances is not None and intolerances != "":
        # remove ',[,] from string
        intolerances = intolerances.replace(",", "")
        intolerances = intolerances.replace("'", "")
        intolerances = intolerances.replace('"', "")
        intolerances = intolerances.replace("%27", "")
        intolerances = intolerances.replace("]", "")
        intolerances = intolerances.replace("[", "")

        intolerances = [intolerance for intolerance in intolerances.split(",")]

        print("intolerances")
        print(intolerances)
        print(intolerances)

        intolerance_objects = Intolerance.objects.filter(name__in=intolerances)
        intolerance_ids = [intolerance.id for intolerance in intolerance_objects]
        print("intolerance_ids")
        print(intolerance_ids)
        ingredient.intolerances.set(intolerance_ids)

    if physical_viscosity:
        ingredient.physical_viscosity = physical_viscosity

    if physical_density:
        ingredient.physical_density = physical_density

    if child_frendly_score:
        ingredient.child_frendly_score = child_frendly_score

    if scout_frendly_score:
        ingredient.scout_frendly_score = scout_frendly_score

    if request.method == "POST":
        form = IngredientFormUpdateAttribute(request.POST, instance=ingredient)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/overview")
    form = IngredientFormUpdateAttribute(instance=ingredient)

    context = {
        "ingredient": ingredient,
        "form": form,
        "url_variable": "ingredient-suggestions-attribute",
    }
    return render(request, "ingredient/update.html", context)


@login_required
def ingredient_update_ref(request, slug):
    instance = get_object_or_404(Ingredient, slug=slug)
    if request.method == "POST":
        form = IngredientFormUpdateRef(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{instance.slug}/overview")
    form = IngredientFormUpdateRef(instance=instance)

    context = {"ingredient": instance, "form": form, "url_variable": False}
    return render(request, "ingredient/update.html", context)


@login_required
def ingredient_update_nutrition(request, slug):
    ingredient = get_object_or_404(Ingredient, slug=slug)
    meta_info = ingredient.meta_info

    energy_kj = float(request.GET.get("energy_kj", "0").replace(",", "."))
    protein_g = float(request.GET.get("protein_g", "0").replace(",", "."))
    fat_g = float(request.GET.get("fat_g", "0").replace(",", "."))
    fat_sat_g = float(request.GET.get("fat_sat_g", "0").replace(",", "."))
    sugar_g = float(request.GET.get("sugar_g", "0").replace(",", "."))
    sodium_mg = float(request.GET.get("sodium_mg", "0").replace(",", "."))
    fruit_factor = float(request.GET.get("fruit_factor", "0").replace(",", "."))
    carbohydrate_g = float(request.GET.get("carbohydrate_g", "0").replace(",", "."))
    fibre_g = float(request.GET.get("fibre_g", "0").replace(",", "."))

    if energy_kj:
        meta_info.energy_kj = energy_kj

    if protein_g:
        meta_info.protein_g = protein_g

    if fat_g:
        meta_info.fat_g = fat_g

    if fat_sat_g:
        meta_info.fat_sat_g = fat_sat_g

    if sugar_g:
        meta_info.sugar_g = sugar_g

    if sodium_mg:
        meta_info.sodium_mg = sodium_mg

    if fruit_factor:
        meta_info.fruit_factor = fruit_factor

    if carbohydrate_g:
        meta_info.carbohydrate_g = carbohydrate_g

    if fibre_g:
        meta_info.fibre_g = fibre_g

    if request.method == "POST":
        form = IngredientFormUpdateNutrition(request.POST, instance=meta_info)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/analyse")
    form = IngredientFormUpdateNutrition(instance=meta_info)

    context = {
        "ingredient": ingredient,
        "form": form,
        "url_variable": "ingredient-suggestions-nutrition",
    }
    return render(request, "ingredient/update.html", context)


@login_required
def ingredient_detail(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    portion_ids = [portion.id for portion in ingredient.portions.all()]
    lastest_price = (
        Price.objects.filter(portion_id__in=portion_ids).order_by("created_at").last()
    )

    print("lastest_price")
    print(lastest_price)

    # get the recipes from recipe items, portions and ingredients
    recipes = Recipe.objects.filter(
        recipe_items__portion__ingredient=ingredient
    ).distinct()

    context = {
        "ingredient": ingredient,
        "module_name": "Detail",
        "lastest_package_price": lastest_price,
        "recipes": recipes,
    }
    return render(request, "ingredient/detail/main.html", context)


@login_required
def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    search_form = SearchForm(
        request.GET
        or {
            "query": "",
            "physical_viscosity": "",
            "retail_section": "",
            "status": "",
        }
    )

    if search_form.is_valid():
        if (
            search_form.cleaned_data["query"]
            and search_form.cleaned_data["query"] is not None
        ):
            ingredients = ingredients.filter(
                name__icontains=search_form.cleaned_data["query"]
            )
        if (
            search_form.cleaned_data["physical_viscosity"]
            and search_form.cleaned_data["physical_viscosity"] is not None
        ):
            ingredients = ingredients.filter(
                physical_viscosity=search_form.cleaned_data["physical_viscosity"]
            )
        if (
            search_form.cleaned_data["retail_section"]
            and search_form.cleaned_data["retail_section"] is not None
            and search_form.cleaned_data["retail_section"] != "Alle"
        ):
            ingredients = ingredients.filter(
                retail_section=search_form.cleaned_data["retail_section"]
            )
        if (
            search_form.cleaned_data["status"]
            and search_form.cleaned_data["status"] is not None
        ):
            if search_form.cleaned_data["status"] != "Alle":
                ingredients = ingredients.filter(
                    status=search_form.cleaned_data["status"]
                )
            else:
                # When "Alle" is selected, show all statuses except "draft"
                ingredients = ingredients.exclude(status="draft")
        else:
            # Default behavior when no status is selected: exclude draft
            ingredients = ingredients.exclude(status="draft")

    order_by = request.GET.get("order_by", "name")
    if order_by == "alpha":
        ingredients = ingredients.order_by("name")
    elif order_by == "popularity":
        ingredients = ingredients.order_by("-recipe_counts")
    elif order_by == "price_asc":
        ingredients = ingredients.order_by("meta_info__price_per_kg")
    elif order_by == "price_desc":
        ingredients = ingredients.order_by("-meta_info__price_per_kg")

    paginator = Paginator(ingredients, per_page=10)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "page_obj": page_obj,
        "module_name": "Liste",
        "form": search_form,
    }
    return render(request, "ingredient/list/main.html", context)


@login_required
def recipe_list(request):
    recipes = Recipe.objects.all()
    search_form = SearchRecipeForm(request.GET)

    if search_form.is_valid():
        if (
            search_form.cleaned_data["query"]
            and search_form.cleaned_data["query"] is not None
        ):
            recipes = recipes.filter(name__icontains=search_form.cleaned_data["query"])
        # filter recipe_type
        if (
            search_form.cleaned_data["recipe_type"]
            and search_form.cleaned_data["recipe_type"] is not None
        ):
            recipes = recipes.filter(
                recipe_type=search_form.cleaned_data["recipe_type"]
            )

        if (
            search_form.cleaned_data["status"]
            and search_form.cleaned_data["status"] is not None
        ):
            if search_form.cleaned_data["status"] != "Alle":
                recipes = recipes.filter(status=search_form.cleaned_data["status"])
            else:
                # When "Alle" is selected, show all statuses except "simulator"
                ecipes = recipes.exclude(status="simulator")
        else:
            # Default behavior when no status is selected: exclude simulator
            recipes = recipes.exclude(status="simulator")

    paginator = Paginator(recipes, per_page=10)
    page_num = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_num)
    page_obj.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "page_obj": page_obj,
        "module_name": "Liste",
        "form": search_form,
    }
    return render(request, "recipe/list/main.html", context)


@login_required
def recipe_create(request):
    meta_info = MetaInfo.objects.create()
    data = {
        "name": None,
        "slug": f"sim-{str(random.randint(1, 100000))}",
        "description": None,
        "status": "simulator",
        "meta_info": meta_info,
    }
    recipe = Recipe(**data)
    recipe.save()

    return HttpResponseRedirect(f"/food/recipe/{recipe.slug}/overview")


@login_required
def recipe_update(request, slug):
    instance = get_object_or_404(Recipe, slug=slug)
    if request.method == "POST":
        form = RecipeFormUpdate(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/recipe/{instance.slug}/overview")
    form = RecipeFormUpdate(instance=instance)

    context = {
        "recipe": instance,
        "form": form,
    }
    return render(request, "create_update_form.html", context)


@login_required
def recipe_clone(request, slug):
    recipe_old = Recipe.objects.get(slug=slug)

    meta_info = deepcopy(recipe_old.meta_info)
    data = {
        "name": "Kopie von " + recipe_old.name,
        "slug": f"copy-{str(random.randint(1, 100000))}",
        "description": "",
        "status": "simulator",
        "meta_info": meta_info,
    }
    recipe = Recipe(**data)
    recipe.save()

    # add the recipe items
    for recipe_item in RecipeItem.objects.filter(recipe=recipe_old):
        recipe_item.pk = None
        recipe_item.recipe = recipe
        recipe_item.save()

    # Clone the metadata
    recipe.meta_info = MetaInfo.objects.create(
        energy_kj=recipe_old.meta_info.energy_kj,
        protein_g=recipe_old.meta_info.protein_g,
        fat_g=recipe_old.meta_info.fat_g,
        fat_sat_g=recipe_old.meta_info.fat_sat_g,
        carbohydrate_g=recipe_old.meta_info.carbohydrate_g,
        sugar_g=recipe_old.meta_info.sugar_g,
        fibre_g=recipe_old.meta_info.fibre_g,
        sodium_mg=recipe_old.meta_info.sodium_mg,
        fruit_factor=recipe_old.meta_info.fruit_factor,
        nutri_score=recipe_old.meta_info.nutri_score,
        nutri_class=recipe_old.meta_info.nutri_class,
        weight_g=recipe_old.meta_info.weight_g,
        price_per_kg=recipe_old.meta_info.price_per_kg,
        price_eur=recipe_old.meta_info.price_eur,
    )
    recipe.save()

    # Update all recipe items with proper meta info
    for recipe_item in recipe.recipe_items.all():
        original_item = RecipeItem.objects.filter(
            recipe=recipe_old, portion=recipe_item.portion
        ).first()
        if original_item:
            recipe_item.meta_info = MetaInfo.objects.create(
                weight_g=original_item.meta_info.weight_g,
                price_per_kg=original_item.meta_info.price_per_kg,
                price_eur=original_item.meta_info.price_eur,
            )
            recipe_item.save()

    # Update recipe's total values
    update_recipe(recipe)

    return HttpResponseRedirect(f"/food/recipe/{recipe.slug}/overview")


@login_required
def recipe_scale(request, slug):
    if request.method == "POST":
        recipe_old = Recipe.objects.get(slug=slug)

        # Get the current total energy
        current_total_energy = recipe_old.meta_info.energy_kj

        # If there's energy to scale
        if current_total_energy > 0 and recipe_old.recipe_type == "warm_lunch":
            # Calculate the scaling factor
            scaling_factor = 3000 / current_total_energy

            # Update all recipe items
            for recipe_item in recipe_old.recipe_items.all():
                # Scale the quantity
                recipe_item.quantity = round(recipe_item.quantity * scaling_factor, 1)
                recipe_item.save()

            # Update the recipe meta info
            update_recipe(recipe_old)

            messages.success(
                request,
                f"Rezept wurde auf 2466 kJ skaliert (Faktor: {scaling_factor:.2f})",
            )
        else:
            messages.error(
                request,
                f"""
                    Skalierung nicht möglich. {recipe_old.name} hat keine
                    Energie oder ist kein warmes Gericht.
                """,
            )

        return HttpResponseRedirect(f"/food/recipe/{slug}/overview")

    # For GET requests, just redirect to recipe overview
    return HttpResponseRedirect(f"/food/recipe/{slug}/overview")

@login_required
def recipe_delete(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    
    if request.method == "POST":
        # Store the recipe name for confirmation message
        recipe_name = recipe.name
        
        # Delete the recipe
        recipe.delete()
        
        # Add success message
        messages.success(request, f"Rezept '{recipe_name}' wurde erfolgreich gelöscht.")
        
        # Redirect to recipe list
        return HttpResponseRedirect("/food/recipe-list/")
    
    # If GET request, show confirmation page
    context = {
        "recipe": recipe,
        "module_name": "Löschen",
    }
    return render(request, "recipe/delete/confirm.html", context)


@login_required
def recipe_detail_overview(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    kpi_price = f"{recipe.meta_info.price_eur:.2f} €"
    kpi_weight = f"{recipe.meta_info.weight_g:.1f} g"
    kpi_nutri_class = recipe.meta_info.nutri_score_display
    kpi_popularity = 1
    kpi_ingredient_count = recipe.recipe_items.count()

    # energy_kj, protein_g, sugar_g, fibre_g kpis
    kpi_energy_kj = f"{recipe.meta_info.energy_kj:.0f} kJ"
    kpi_protein_g = (
        f"{recipe.meta_info.protein_g:.1f} g - {recipe.meta_info.protein_g / recipe.meta_info.weight_g * 100:.0f}%"
        if recipe.meta_info.weight_g != 0
        else f"{recipe.meta_info.protein_g:.1f} g"
    )
    kpi_sugar_g = (
        f"{recipe.meta_info.sugar_g:.1f} g - {recipe.meta_info.sugar_g / recipe.meta_info.weight_g * 100:.0f}%"
        if recipe.meta_info.weight_g != 0
        else f"{recipe.meta_info.sugar_g:.1f} g"
    )
    kpi_fibre_g = (
        f"{recipe.meta_info.fibre_g:.1f} g - {recipe.meta_info.fibre_g / recipe.meta_info.weight_g * 100:.0f}%"
        if recipe.meta_info.weight_g != 0
        else f"{recipe.meta_info.fibre_g:.1f} g"
    )

    context = {
        "recipe": recipe,
        "module_name": "Detail",
        "ingredients": Ingredient.objects.all(),
        "kpi_price": kpi_price,
        "kpi_weight": kpi_weight,
        "kpi_nutri_class": kpi_nutri_class,
        "kpi_popularity": kpi_popularity,
        "kpi_ingredient_count": kpi_ingredient_count,
        "kpi_energy_kj": kpi_energy_kj,
        "kpi_protein_g": kpi_protein_g,
        "kpi_sugar_g": kpi_sugar_g,
        "kpi_fibre_g": kpi_fibre_g,
    }
    return render(request, "recipe/detail/overview/main.html", context)


@login_required
def recipe_detail_analyse(request, slug):
    recipe = Recipe.objects.get(slug=slug)
    recipe_items = RecipeItem.objects.filter(recipe=recipe)

    context = {
        "recipe": recipe,
        "module_name": "Analyse",
        "recipe_items": recipe_items,
    }
    return render(request, "recipe/detail/analyse/main.html", context)


@login_required
def recipe_detail_shopping(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    # Get the quantity parameter from the request, default to 1
    quantity = request.GET.get("quantity", 1)
    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        quantity = 1

    # Get recipe ingredients
    recipe_ingredients = RecipeItem.objects.filter(recipe=recipe)

    # Calculate aggregate values
    total_weight_g = sum(item.meta_info.weight_g for item in recipe_ingredients)
    total_price_eur = sum(item.meta_info.price_eur for item in recipe_ingredients)

    context = {
        "recipe": recipe,
        "module_name": "Einkauf",
        "recipe_ingredients": recipe_ingredients,
        "quantity": quantity,
        "total_weight_g": total_weight_g,
        "total_price_eur": total_price_eur,
    }
    return render(request, "recipe/detail/shopping/main.html", context)


@login_required
def recipe_detail_comment(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    context = {
        "recipe": recipe,
        "module_name": "Kommentare",
        "ingredients": Ingredient.objects.all(),
    }
    return render(request, "recipe/detail/comment/main.html", context)


@login_required
def recipe_detail_manage(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    context = {
        "recipe": recipe,
        "module_name": "Verwalten",
    }
    return render(request, "recipe/detail/manage/main.html", context)


@login_required
def recipes(request):
    recipes = Recipe.objects.filter(status="verified")
    context = {
        "recipes": recipes,
    }
    return render(request, "recipe/main.html", context)


@login_required
def recipe_item_create(request, slug):
    if request.method == "POST":
        recipe = Recipe.objects.get(slug=slug)
        ingredient_id = request.POST.get("ingredient")
        form = RecipeItemFormCreate(
            data={
                "recipe": recipe,
                "portion": Portion.objects.filter(ingredient_id=ingredient_id)
                .order_by("rank")
                .first()
                .id,
                "quantity": 100,
            }
        )

        if form.is_valid():
            data = form.cleaned_data

            # create a new post
            recipe_item = RecipeItem(**data)
            recipe_item.created_by = request.user
            # add meta info
            new_meta_info = MetaInfo.objects.create()
            recipe_item.meta_info = new_meta_info
            recipe_item.save()

            update_recipe(recipe)

            return HttpResponseRedirect(
                f"/food/recipe/{recipe_item.recipe.slug}/overview"
            )


@login_required
def recipe_item_update(request, slug):
    if request.method == "POST":
        recipe = Recipe.objects.get(slug=slug)
        form = RecipeItemFormUpdate(
            data={
                "recipe_item_id": request.POST.get("recipe_item_id"),
                "recipe_id": recipe.id,
                "portion_id": Portion.objects.get(
                    pk=request.POST.get("portion_update")
                ).id,
                "quantity": int(request.POST.get("quantity")),
            }
        )

        if form.is_valid():
            data = form.cleaned_data
            recipe_item = RecipeItem.objects.get(pk=data["recipe_item_id"])
            recipe_item.portion = Portion.objects.get(pk=data["portion_id"])
            recipe_item.quantity = data["quantity"]
            recipe_item.save()

            update_recipe(recipe)

            return HttpResponseRedirect(
                f"/food/recipe/{recipe_item.recipe.slug}/overview"
            )


@login_required
def recipe_item_delete(request):
    if request.method == "POST":
        recipe_item_id = request.POST.get("recipe_item_id")
        recipe_item = RecipeItem.objects.get(pk=recipe_item_id)
        recipe = recipe_item.recipe
        recipe_item.delete()

        update_recipe(recipe)

        return HttpResponseRedirect(f"/food/recipe/{recipe.slug}/")


@login_required
def recipe_update_meta_infos(request, slug):
    recipe = Recipe.objects.get(slug=slug)
    recipe_items = RecipeItem.objects.filter(recipe=recipe)

    if request.method == "POST":
        update_recipe(recipe)
        update_meta_info_nutri(recipe, recipe_items)

        messages.success(request, "Die Nährwerte wurden erfolgreich aktualisiert.")

        return HttpResponseRedirect(f"/food/recipe/{recipe.slug}/overview")


@login_required
def ingredient_portion_create(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)
    if request.method == "POST":
        form = PortionFormCreate(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            data["ingredient"] = ingredient

            new_meta_info = MetaInfo.objects.create(
                weight_g=data["quantity"]
                * data["measuring_unit"].quantity,  # todo: handle ml also here
                price_per_kg=ingredient.meta_info.price_per_kg,
                price_eur=ingredient.meta_info.price_per_kg
                * (data["quantity"] * data["measuring_unit"].quantity / 1000),
            )
            data["meta_info"] = new_meta_info

            portion = Portion(**data)
            portion.save()

            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/")
    form = PortionFormCreate()

    context = {
        "ingredient": ingredient,
        "form": form,
    }
    return render(request, "ingredient/portion/create.html", context)


@login_required
def ingredient_portion_update(request, slug, pk):
    ingredient = Ingredient.objects.get(slug=slug)
    portion = Portion.objects.get(pk=pk)
    if request.method == "POST":
        form = PortionFormUpdate(request.POST, instance=portion)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/")
    form = PortionFormUpdate(instance=portion)

    context = {
        "ingredient": ingredient,
        "form": form,
    }
    return render(request, "ingredient/portion/update.html", context)


@login_required
def ingredient_price_create(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)
    if request.method == "POST":
        form = PriceForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data

            price = Price(**data)
            price.save()

            return HttpResponseRedirect(f"ingredient/{ingredient.slug}/portion/")
    form = PriceForm()
    form.fields["portion"].queryset = Portion.objects.filter(ingredient=ingredient)

    context = {
        "ingredient": ingredient,
        "form": form,
    }
    return render(request, "ingredient/price/create.html", context)


def update_price_in_portions(ingredient, price_per_kg):

    MetaInfo.objects.filter(
        id__in=[
            portion.meta_info.id
            for portion in Portion.objects.filter(ingredient=ingredient)
        ]
    ).update(price_per_kg=price_per_kg)

    # update the price of the ingredient
    MetaInfo.objects.filter(id=ingredient.meta_info.id).update(
        price_per_kg=price_per_kg
    )

    return True


def ingredient_price_update(request, slug, pk):
    ingredient = Ingredient.objects.get(slug=slug)
    price = Price.objects.get(pk=pk)
    if request.method == "POST":
        form = PriceFormUpdate(request.POST, instance=price)

        if form.is_valid():
            price_per_kg = form.cleaned_data["price_eur"] / (
                price.portion.meta_info.weight_g * 1000
            )
            update_price_in_portions(ingredient, price_per_kg)
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/portion")
    form = PriceFormUpdate(instance=price)
    form.fields["portion"].queryset = Portion.objects.filter(ingredient=ingredient)

    context = {
        "ingredient": ingredient,
        "form": form,
    }
    return render(request, "ingredient/price/update.html", context)


@login_required
def ingredient_detail_overview(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    context = {
        "ingredient": ingredient,
        "module_name": "Detail",
    }
    return render(request, "ingredient/detail/overview/main.html", context)


@login_required
def ingredient_detail_analyse(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    context = {
        "ingredient": ingredient,
        "module_name": "Analyse",
    }
    return render(request, "ingredient/detail/analyse/main.html", context)


@login_required
def ingredient_detail_portion(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    context = {
        "ingredient": ingredient,
        "module_name": "Portionen",
        "prices": Price.objects.filter(portion__ingredient=ingredient).order_by(
            "-created_at",
        ),
    }
    return render(request, "ingredient/detail/portion/main.html", context)


@login_required
def ingredient_detail_recipe(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)
    ingredients = Ingredient.objects.all().exclude(slug=slug).order_by("?")[0:5]
    recipes = Recipe.objects.filter(
        recipe_items__portion__ingredient=ingredient, status="verified"
    ).distinct()

    context = {
        "ingredient": ingredient,
        "ingredients": ingredients,
        "recipes": recipes,
        "module_name": "Rezepte",
    }
    return render(request, "ingredient/detail/recipe/main.html", context)


def display_name(portion):
    if portion.name:
        return f"{portion.name} in {portion.measuring_unit.name}"
    return f"{portion.ingredient.name} in {portion.measuring_unit.name}"


@login_required
def get_portions_by_ingredient(request):

    if request.method == "POST":
        ingredient_slug = request.POST.get("ingredient")
        data = {"portions": []}
        if request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest":

            portions = None
            if ingredient_slug:
                portions = Portion.objects.filter(ingredient__slug=ingredient_slug)

            if not portions:
                return JsonResponse(data)

            for portion in portions:
                data["portions"].append(
                    {
                        "id": portion.id,
                        "display_name": display_name(portion),
                    }
                )

            return JsonResponse(data)


@login_required
def ingredient_suggestions_basic(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    retail_sections = RetailSection.objects.all()

    # create list from retail_sections
    retail_sections = [section.name for section in retail_sections]

    class OutputModel(BaseModel):
        name: str = Field(
            min_length=5,
            max_length=1000,
            description="name der Zutat. Kurz und prägnant. Ohne Mengenangaben. Ohne Sonderzeichen. Ohne Werbung. Ohne Markennamen.",
        )
        description: str = Field(
            min_length=5,
            max_length=1000,
            description="Beschreibung der Zutat. Kurz und prägnant. Ohne Mengenangaben. Ohne Sonderzeichen.",
        )
        retail_section: str = Field(
            description=f"Einzelhandelsbereich der Zutat. Z.B. {', '.join(retail_sections)}",
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende technisch genaue Texte für die Rezepzutat
            ohne Werbung. Sehr sachlich. Kurz. Konkret.
            Entferne alle Mengenangaben und Einheiten. Ohne Markennamen.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    output = output.model_dump()

    # set retail_section id to the ingredient
    if output["retail_section"] in retail_sections:
        retail_section = RetailSection.objects.get(name=output["retail_section"])
        ingredient.retail_section = retail_section

    context = {
        "output": output,
    }
    return render(request, "ingredient/detail/suggestions/basic.html", context)


@login_required
def ingredient_suggestions_attribute(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    intolerances = Intolerance.objects.all()

    # create list from retail_sections
    intolerances_list = [intolerance.name for intolerance in intolerances]

    class OutputModel(BaseModel):
        intolerances: List[str] = Field(
            description=f"Essens Unverträglichkeiten der Zutat. aus der Liste {', '.join(intolerances_list)}",
        )
        physical_viscosity: str = Field(
            description="Physikalische Viskosität der Zutat. 'solid' oder 'beverage'",
        )
        physical_density: str = Field(
            description="ungefähre physikalische Dichte der Zutat in g/cm³",
        )
        child_frendly_score: str = Field(
            description="Wie sehr würden sich Kinder darüber freuen diese Zutat zu essen auf einer Skala von 1 bis 5. Wobei 1 sehr wenig und 5 sehr viel bedeutet.",
        )
        scout_frendly_score: str = Field(
            description="Pfadfinderfreundlichkeit der Zutat auf einer Skala von 1 bis 5. Wobei 1 sehr wenig und 5 sehr viel bedeutet.",
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende technisch genaue Texte für die Rezepzutat
            ohne Werbung. Sehr sachlich. Kurz. Konkret.
            Entferne alle Mengenangaben und Einheiten. Ohne Markennamen.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    output = output.model_dump()

    context = {
        "output": output,
    }
    return render(request, "ingredient/detail/suggestions/basic.html", context)


@login_required
def ingredient_suggestions_nutrition(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    class OutputModel(BaseModel):
        energy_kj: float = Field(
            description="Energiegehalt in kJ pro 100g",
        )
        protein_g: float = Field(
            description="Proteingehalt in g pro 100g",
        )
        protein_g: float = Field(
            description="Proteingehalt in g pro 100g",
        )
        fat_g: float = Field(
            description="Fettgehalt in g pro 100g",
        )
        fat_sat_g: float = Field(
            description="Gesättigte Fettsäuren in g pro 100g",
        )
        sodium_mg: float = Field(
            description="Natriumgehalt in mg pro 100g",
        )
        carbohydrate_g: float = Field(
            description="Kohlenhydratgehalt in g pro 100g",
        )
        sugar_g: float = Field(
            description="Zuckergehalt in g pro 100g",
        )
        fibre_g: float = Field(
            description="Ballaststoffgehalt in g pro 100g",
        )
        fruit_factor: float = Field(
            description="Obst Gemüse faktor der Zutat für den Nutriscore berechnung. Von 0.0 bis 1.0",
        )

    output = get_ai_suggestion(
        prompt=f"""
            Gebe mir passende Nährwerte für die Rezepzutat. Falls nicht bekannt, dann schätze die Werte.
            {ingredient.name} {ingredient.description}
        """,
        model="models/gemini-2.0-flash-exp",
        OutputModel=OutputModel,
    )

    output = output.model_dump()

    context = {
        "output": output,
    }
    return render(request, "ingredient/detail/suggestions/basic.html", context)


@login_required
def meal_detail(request, slug, id):
    plan = MealEvent.objects.get(slug=slug)
    meal = Meal.objects.get(id=id)

    context = {
        "meal": meal,
        "plan": plan,
        "module_name": "Menü",
    }
    return render(request, "meal/detail/main.html", context)


def admin_main(request):
    return render(request, "plan/admin/main.html")


@login_required
def search_results_view(request):
    query = request.GET.get("search", "")

    all_data = Ingredient.objects.all()
    if query and len(query) >= 3:
        all_data = all_data.filter(name__icontains=query)
        context = {"data": all_data[:10], "count": all_data.count()}
    else:
        all_data = []
        context = {"data": all_data, "count": 0}

    return render(request, "recipe/detail/overview/search_results.html", context)
