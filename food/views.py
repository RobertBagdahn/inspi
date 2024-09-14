from django.db.models import Q, QuerySet
from django_filters import CharFilter, NumberFilter
from food.choices import Gender
from django.shortcuts import render
from django.http import HttpResponseRedirect

from copy import deepcopy
from itertools import groupby
from datetime import date, timedelta
import datetime

from general.login.models import CustomUser as User

from .forms import MealEventForm, SearchForm, IngredientFilterForm
from .models import (
    MealEvent,
    Recipe,
    Ingredient,
    MealEventTemplate,
    Package,
    PackagePrice,
)


# create view with template main.html


def mainView(request):
    famous_meal_events = MealEvent.objects.all()[0:3]
    famous_recipes = Recipe.objects.filter(status="verified").order_by("id")[0:3]
    famous_ingredients = Ingredient.objects.all()[0:3]

    context = {
        "famous_meal_events": famous_meal_events,
        "famous_recipes": famous_recipes,
        "famous_ingredients": famous_ingredients,
    }
    return render(request, "main.html", context)


def plan(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
    }
    return render(request, "plan.html", context)


def plan_editor(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Editor",
    }
    return render(request, "plan-editor.html", context)


def plan_overview(request):
    plans = MealEvent.objects.all()
    context = {
        "plans": plans,
    }
    return render(request, "plan-overview.html", context)


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
            plan.author = User.objects.first()
            plan.save()
            for category in categories:
                plan.categories.add(category)

            return HttpResponseRedirect("/food/plan-list/")

        return render(request, "plan-create.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MealEventForm()
        return render(request, "plan-create.html", {"form": form})


def plan_dashboard(request):
    plans = MealEvent.objects.all()
    context = {
        "plans": plans,
    }
    return render(request, "plan-dashboard.html", context)


def template_create(request):
    return render(request, "template-create.html")


def meal_event_create(request):
    templates = MealEventTemplate.objects.all()
    context = {
        "templates": templates,
    }
    return render(request, "meal-event-create.html", context)


def meal_event_clone(request):
    mealEvents = MealEvent.objects.all()
    context = {
        "mealEvents": mealEvents,
    }
    return render(request, "meal-event-clone.html", context)


def plan_shopping_cart(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    shopping_list = [
        {
            "ingredient_name": "Tomate",
            "ingredient_class": "Gemüse",
            "recipe_name": "Tomatensoße",
            "price": 1.91,
            "weight_show": "2 Kg",
        },
        {
            "ingredient_name": "Nudeln",
            "ingredient_class": "Gemüse",
            "recipe_name": "Tomatensoße",
            "price": 0.99,
            "weight_show": "500 g",
        },
    ]

    context = {
        "plan": plan,
        "shopping_list": shopping_list,
        "module_name": "Einkaufsliste",
    }
    return render(request, "plan/shopping-list.html", context)


def plan_participants(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    context = {"plan": plan, "module_name": "Teilnehmer"}
    return render(request, "plan/participants.html", context)


def ingredient_create(request):
    return render(request, "ingredient/create.html")


def ingredient_detail(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    portion_ids = [portion.id for portion in ingredient.portions.all()]
    packages = Package.objects.filter(portion__in=portion_ids)
    lastest_package_price = (
        PackagePrice.objects.filter(package__in=packages).order_by("created_at").last()
    )

    # get the recipes from recipe items, portions and ingredients
    recipes = (
        Recipe.objects.filter(recipe_items__portion__ingredient=ingredient)
        .filter(status="verified")
        .distinct()
    )

    context = {
        "ingredient": ingredient,
        "module_name": "Detail",
        "lastest_package_price": lastest_package_price,
        "recipes": recipes,
    }
    return render(request, "ingredient/detail/main.html", context)


def ingredient_list(request):
    ingredients = Ingredient.objects.all()
    search_form = SearchForm(request.GET)
    filter_form = IngredientFilterForm(request.GET)

    if search_form.is_valid():
        if (
            search_form.cleaned_data["query"]
            and search_form.cleaned_data["query"] is not None
        ):
            ingredients = ingredients.filter(
                name__icontains=search_form.cleaned_data["query"]
            )

    if filter_form.is_valid():
        if (
            filter_form.cleaned_data["physical_viscosity"]
            and filter_form.cleaned_data["physical_viscosity"] is not None
        ):
            ingredients = ingredients.filter(
                physical_viscosity=filter_form.cleaned_data["physical_viscosity"]
            )

    context = {
        "ingredients": ingredients,
        "module_name": "Liste",
        "search_form": search_form,
        "filterForm": filter_form,
    }
    return render(request, "ingredient/list/main.html", context)


def recipe_list(request):
    recipes = Recipe.objects.all()
    search_form = SearchForm(request.GET)

    if search_form.is_valid():
        if (
            search_form.cleaned_data["query"]
            and search_form.cleaned_data["query"] is not None
        ):
            recipes = recipes.filter(name__icontains=search_form.cleaned_data["query"])

    context = {
        "recipes": recipes,
        "module_name": "Liste",
        "search_form": search_form,
    }
    return render(request, "recipe/list/main.html", context)


def recipe_detail(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    context = {
        "recipe": recipe,
        "module_name": "Detail",
    }
    return render(request, "recipe/detail/main.html", context)


def recipes(request):
    recipes = Recipe.objects.filter(status="verified")
    context = {
        "recipes": recipes,
    }
    return render(request, "recipe/main.html", context)
