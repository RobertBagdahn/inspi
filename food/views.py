from django_filters import CharFilter, NumberFilter
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from copy import deepcopy

from general.login.models import CustomUser
import random

from .forms import (
    MealEventForm,
    SearchForm,
    IngredientFilterForm,
    MealEventTemplateFormCreate,
    MealEventTemplateFormUpdate,
    IngredientForm,
    PortionFormCreate,
    PortionFormUpdate,
    PriceForm,
    PriceFormUpdate,
    IngredientFormUpdate,
    RecipeItemFormCreate,
    RecipeItemFormUpdate,
    RecipeFormUpdate,
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
)


# create view with template main.html

@login_required
def mainView(request):
    famous_meal_events = MealEvent.objects.all()[0:3]
    famous_recipes = Recipe.objects.order_by("id")[0:3] # add .filter(status="verified")
    famous_ingredients = Ingredient.objects.all()[0:3]

    context = {
        "famous_meal_events": famous_meal_events,
        "famous_recipes": famous_recipes,
        "famous_ingredients": famous_ingredients,
    }
    return render(request, "main.html", context)

@login_required
def plan(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
    }
    return render(request, "plan.html", context)

@login_required
def plan_editor(request, slug):
    plan = MealEvent.objects.get(slug=slug)
    context = {
        "plan": plan,
        "module_name": "Editor",
    }
    return render(request, "plan-editor.html", context)

@login_required
def plan_overview(request):
    plans = MealEvent.objects.all()
    context = {
        "plans": plans,
    }
    return render(request, "plan-overview.html", context)

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

        return render(request, "plan-create.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = MealEventForm()
        return render(request, "plan-create.html", {"form": form})

@login_required
def plan_dashboard(request):
    plans = MealEvent.objects.all()
    context = {
        "plans": plans,
    }
    return render(request, "plan-dashboard.html", context)

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
                template.intolerances.add(intolerance)
            
            for template_option in template_options:
                template.template_options.add(template_option)

            event_name = f"{template.name}-{str(random.randint(1, 10000))}"
            event_name_slug = event_name.replace(" ", "-").lower()
            # create meal events from template
            new_meal_event = MealEvent.objects.create(
                # add random number to name
                event_name = event_name,
                slug = event_name_slug,
                description = template.description,
                meal_event_template = template,
                norm_portions = 1,
                reserve_factor = 1.0,
                activity_factor = 'Z',
                is_public = template.is_public,
                is_approved = False,
            )
            # add meta info
            new_meta_info = MetaInfo.objects.create()
            new_meal_event.meta_info = new_meta_info
            new_meal_event.save()

            # add three meal_day
            for i in range(1, 4):
                new_meal_day = MealDay.objects.create(
                    meal_event = new_meal_event,
                    max_day_part_factor = 1.0,
                )
                # add meta info
                new_meta_info = MetaInfo.objects.create()
                new_meal_day.meta_info = new_meta_info
                new_meal_day.save()

                meal_types = [
                    {
                        'name': 'Tagesgetränke',
                        'meal_type': 'drinks',
                        'day_part_factor': 1.0,
                    },
                    {
                        'name': 'Tages-Snacks',
                        'meal_type': 'snacks',
                        'day_part_factor': 1.0,
                    },
                    {
                        'name': 'Frühstück',
                        'meal_type': 'breakfast',
                        'day_part_factor': 1.0,
                        'time_start': '07:00',
                        'time_end': '08:00',
                    },
                    {
                        'name': 'Mittagessen',
                        'meal_type': 'lunch',
                        'day_part_factor': 1.0,
                        'time_start': '12:00',
                        'time_end': '13:00',
                    },
                    {
                        'name': 'Abendessen',
                        'meal_type': 'dinner',
                        'day_part_factor': 1.0,
                        'time_start': '18:00',
                        'time_end': '19:00',
                    },
                    {
                        'name': 'Abend-Snacks',
                        'meal_type': 'evening_snacks',
                        'day_part_factor': 1.0,
                        'time_start': '21:00',
                        'time_end': '22:00',
                    },
                ]
                for meal_type in meal_types:
                    new_meal = Meal.objects.create(
                        meal_day = new_meal_day,
                        name = meal_type['name'],
                        meal_type = meal_type['meal_type'],
                        day_part_factor = meal_type['day_part_factor'],
                        time_start = meal_type.get('time_start', None),
                        time_end = meal_type.get('time_end', None),
                    )
                    # add meta info
                    new_meta_info = MetaInfo.objects.create()
                    new_meal.meta_info = new_meta_info
                    new_meal.save()

                    # add a random recipe
                    recipes = Recipe.objects.all()
                    random_recipe = recipes[random.randint(0, len(recipes) - 1)]

                    new_meal_item = MealItem.objects.create(
                        meal = new_meal,
                        recipe = random_recipe,
                        factor = 1.0,
                    )

                    # add meta info
                    new_meta_info = MetaInfo.objects.create()
                    new_meal_item.meta_info = new_meta_info

                    new_meal_item.save()
            
            return HttpResponseRedirect(f"/food/plan/{event_name_slug}")

    form = MealEventTemplateFormCreate(
        initial={
            "name": "Neue Veranstaltung",
            "description": "",
            "max_price_eur": 7.00,
            "suit_level": "M",
            "warm_meal": "J",
            "animal_products": "VEG",
            "meal_time_options": "SW",
            "child_frendly": "CA",
        }
    )
    return render(request, "template/create.html", {"form": form})

@login_required
def template_update(request, id):
    instance = get_object_or_404(MealEventTemplate, id=id)
    meal_event = MealEvent.objects.get(meal_event_template=instance)
    if request.method == "POST":
        form = MealEventTemplateFormUpdate(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/plan/{meal_event.slug}/")
    form = MealEventTemplateFormUpdate(instance=instance)

    context = {
        "template": instance,
        "form": form,
    }
    return render(request, "template/update.html", context)

@login_required
def meal_event_create(request):
    templates = MealEventTemplate.objects.all()
    context = {
        "templates": templates,
    }
    return render(request, "meal-event-create.html", context)

@login_required
def meal_event_clone(request):
    mealEvents = MealEvent.objects.all()
    context = {
        "mealEvents": mealEvents,
    }
    return render(request, "meal-event-clone.html", context)

@login_required
def plan_shopping_cart(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    shopping_list = [
        {
            "ingredient_name": "Tomate",
            "ingredient_class": "Gemüse",
            "recipe_name": "Tomatensoße mit Nudeln",
            "price": 1.91,
            "weight_show": "1 Kg",
            "pieces": 5,
            "weight_g": 1000,
        },
        {
            "ingredient_name": "Nudeln",
            "ingredient_class": "Teigwaren",
            "recipe_name": "Tomatensoße mit Nudeln",
            "price": 0.99,
            "weight_show": "250 g",
            "pieces": 1,
            "weight_g": 250,
        },
        {
            "ingredient_name": "Tomatenmark",
            "ingredient_class": "Gewürz",
            "recipe_name": "Tomatensoße mit Nudeln",
            "price": 1.99,
            "weight_show": "200 g",
            "weight_g": 200,
        },
        {
            "ingredient_name": "Brühe",
            "ingredient_class": "Soßen",
            "recipe_name": "Tomatensoße mit Nudeln",
            "price": 2.49,
            "weight_show": "500 g",
            "weight_g": 500,
        },
        {
            "ingredient_name": "Salz",
            "ingredient_class": "Gewürz",
            "recipe_name": "Tomatensoße mit Nudeln",
            "price": 3.49,
            "weight_show": "500 g",
            "weight_g": 500,
        },
        {
            "ingredient_name": "Tomaten",
            "ingredient_class": "Gemüse",
            "recipe_name": "Frühstück",
            "price": 3.49,
            "weight_show": "100 g",
            "weight_g": 100,
        },
        {
            "ingredient_name": "Brot",
            "ingredient_class": "Backwaren",
            "recipe_name": "Frühstück",
            "price": 2.49,
            "weight_show": "1 Kg",
            "weight_g": 1000,
        },
    ]

    context = {
        "plan": plan,
        "shopping_list": shopping_list,
        "module_name": "Einkaufsliste",
        "total_price": sum([item["price"] for item in shopping_list]),
    }
    return render(request, "plan/shopping-list.html", context)

@login_required
def plan_participants(request, slug):
    plan = MealEvent.objects.get(slug=slug)

    context = {"plan": plan, "module_name": "Teilnehmer"}
    return render(request, "plan/participants.html", context)

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
                meta_info=new_portion_meta_info
            )

            ingredient.portions.add(new_portion)

            return HttpResponseRedirect("/food/ingredient-list/")

    form = IngredientForm()
    return render(request, "ingredient/create.html", {"form": form})

@login_required
def ingredient_update(request, slug):
    instance = get_object_or_404(Ingredient, slug=slug)
    if request.method == "POST":
        form = IngredientFormUpdate(request.POST, instance=instance)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{instance.slug}/")
    form = IngredientFormUpdate(instance=instance)

    context = {
        "ingredient": instance,
        "form": form,
    }
    return render(request, "ingredient/update.html", context)

@login_required
def ingredient_detail(request, slug):
    ingredient = Ingredient.objects.get(slug=slug)

    portion_ids = [portion.id for portion in ingredient.portions.all()]
    lastest_price = (
        Price.objects.filter(portion_id__in=portion_ids).order_by("created_at").last()
    )

    # get the recipes from recipe items, portions and ingredients
    recipes = (
        Recipe.objects.filter(recipe_items__portion__ingredient=ingredient)
        .distinct()
    )

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

@login_required
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

@login_required
def recipe_create(request):
    meta_info = MetaInfo.objects.create()
    data = {
        "name": "Simulator",
        "slug": f"sim-{str(random.randint(1, 100000))}",
        "description": "Beschreibung",
        "status": "draft",
        "meta_info": meta_info,
    }
    recipe = Recipe(**data)
    recipe.save()

    return HttpResponseRedirect(f"/food/recipe/{recipe.slug}/")

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
    return render(request, "recipe/update.html", context)

@login_required
def recipe_clone(request, slug):
    recipe_old = Recipe.objects.get(slug=slug)

    meta_info = deepcopy(recipe_old.meta_info)
    data = {
        "name": "Kopie von " + recipe_old.name,
        "slug": f"copy-{str(random.randint(1, 100000))}",
        "description": "",
        "status": "draft",
        "meta_info": meta_info,
    }
    recipe = Recipe(**data)
    recipe.save()

    # add the recipe items
    for recipe_item in RecipeItem.objects.filter(recipe=recipe_old):
        recipe_item.pk = None
        recipe_item.recipe = recipe
        recipe_item.save()

    recipe.managed_by.add(CustomUser.objects.first())

    return HttpResponseRedirect(f"/food/recipe/{recipe.slug}/overview")

@login_required
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

@login_required
def recipe_detail_overview(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    context = {
        "recipe": recipe,
        "module_name": "Detail",
        "ingredients": Ingredient.objects.all(),
    }
    return render(request, "recipe/detail/overview/main.html", context)


@login_required
def recipe_detail_analyse(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    context = {
        "recipe": recipe,
        "module_name": "Analyse",
        "ingredients": Ingredient.objects.all(),
    }
    return render(request, "recipe/detail/analyse/main.html", context)

@login_required
def recipe_detail_shopping(request, slug):
    recipe = Recipe.objects.get(slug=slug)

    context = {
        "recipe": recipe,
        "module_name": "Einkauf",
        "ingredients": Ingredient.objects.all(),
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
def recipes(request):
    recipes = Recipe.objects.filter(status="verified")
    context = {
        "recipes": recipes,
    }
    return render(request, "recipe/main.html", context)

@login_required
def recipe_item_create(request, slug):
    if request.method == "POST":
        form = RecipeItemFormCreate(
            data={
                "recipe": Recipe.objects.get(slug=slug),
                "portion": Portion.objects.get(pk=request.POST.get("portion_create")),
                "quantity": request.POST.get("quantity"),
            }
        )

        if form.is_valid():
            print("form is valid")

            data = form.cleaned_data

            # create a new post
            recipe_item = RecipeItem(**data)
            recipe_item.created_by = request.user
            # add meta info
            new_meta_info = MetaInfo.objects.create()
            recipe_item.meta_info = new_meta_info
            recipe_item.save()

            return HttpResponseRedirect(f"/food/recipe/{recipe_item.recipe.slug}/overview")

@login_required
def recipe_item_update(request, slug):
    if request.method == "POST":
        form = RecipeItemFormUpdate(
            data={
                "recipe_item_id": request.POST.get("recipe_item_id"),
                "recipe_id": Recipe.objects.get(slug=slug).id,
                "portion_id": Portion.objects.get(pk=request.POST.get("portion_update")).id,
                "quantity": int(request.POST.get("quantity")),
            }
        )

        if form.is_valid():
            data = form.cleaned_data
            recipe_item = RecipeItem.objects.get(pk=data["recipe_item_id"])
            recipe_item.portion = Portion.objects.get(pk=data["portion_id"])
            recipe_item.quantity = data["quantity"]
            recipe_item.save()

            return HttpResponseRedirect(f"/food/recipe/{recipe_item.recipe.slug}/overview")

@login_required
def recipe_item_delete(request):
    if request.method == "POST":
        recipe_item_id = request.POST.get("recipe_item_id")
        recipe_item = RecipeItem.objects.get(pk=recipe_item_id)
        recipe_slug = recipe_item.recipe.slug
        recipe_item.delete()

        return HttpResponseRedirect(f"/food/recipe/{recipe_slug}/")

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
                price_eur=ingredient.meta_info.price_per_kg * (data["quantity"] * data["measuring_unit"].quantity / 1000),
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
            price.save() # trigger post_save signal

            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/")
    form = PriceForm()
    form.fields["portion"].queryset = Portion.objects.filter(ingredient=ingredient)

    context = {
        "ingredient": ingredient,
        "form": form,
    }
    return render(request, "ingredient/price/create.html", context)

@login_required
def update_price_in_portions(ingredient, price_per_kg):

    MetaInfo.objects.filter(
        id__in=[
            portion.meta_info.id
            for portion in Portion.objects.filter(ingredient=ingredient)
        ]
    ).update(price_per_kg=price_per_kg)

    # update the price of the ingredient
    MetaInfo.objects.filter(
        id=ingredient.meta_info.id
    ).update(price_per_kg=price_per_kg)

    return True

@login_required
def ingredient_price_update(request, slug, pk):
    ingredient = Ingredient.objects.get(slug=slug)
    price = Price.objects.get(pk=pk)
    if request.method == "POST":
        form = PriceFormUpdate(request.POST, instance=price)

        if form.is_valid():
            price_per_kg = form.cleaned_data["price_eur"] / (price.portion.meta_info.weight_g * 1000)
            update_price_in_portions(ingredient, price_per_kg)
            form.save()
            return HttpResponseRedirect(f"/food/ingredient/{ingredient.slug}/")
    form = PriceFormUpdate(instance=price)
    form.fields["portion"].queryset = Portion.objects.filter(ingredient=ingredient)

    context = {
        "ingredient": ingredient,
        "form": form,
    }
    return render(request, "ingredient/price/update.html", context)

@login_required
def get_portions_by_ingredient(request):

    if request.method == "POST":
        ingredient_slug = request.POST.get('ingredient')
        data = {
            "portions": []
        }
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':

            portions = None 
            if ingredient_slug:
                portions = Portion.objects.filter(ingredient__slug=ingredient_slug)

            if not portions:
                return JsonResponse(data)

            for portion in portions:
                data['portions'].append({"id": portion.id, "display_name": f"{portion.name} in {portion.measuring_unit.name}"})

            return JsonResponse(data)
        
@login_required
def meal_detail(request, slug, id):
    plan = MealEvent.objects.get(slug=slug)
    meal = Meal.objects.get(id=id)

    context = {
        "meal": meal,
        "plan": plan,
        "module_name": "Meal Detail",

    }
    return render(request, "meal/detail/main.html", context)