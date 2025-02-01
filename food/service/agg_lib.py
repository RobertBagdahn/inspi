from food import models as food_models
from django.db.models import Sum


def agg_func(obj, agg_field):
    if isinstance(agg_field, str):
        return obj.get(agg_field)
    if isinstance(agg_field, list):
        return obj.get(agg_field[0]) * obj.get(agg_field[1])


def get_agg_recipe(recipes, agg_field):
    total = 0
    recipe_items = recipes.get("recipe_items")
    for recipe_item in recipe_items:
        total += agg_func(recipe_item, agg_field)
    return total


def get_agg_meal_items(meal_items, agg_field):
    total = 0
    recipe = meal_items.get("recipe")
    factor = meal_items.get("factor")
    total += get_agg_recipe(recipe, agg_field) * factor
    return total


def get_agg_meal(meals, agg_field):
    total = 0
    meal_items = meals.get("meal_items")
    for meal_item in meal_items:
        total += get_agg_meal_items(meal_item, agg_field)
    return total

def get_agg_day(meal_days, agg_field):
    total = 0
    meals = meal_days.get("meals")
    for meal in meals:
        total += get_agg_meal(meal, agg_field)
    return total


def get_agg_meal_event(events, agg_field):
    total = 0
    event_values = events.get("meal_days")
    for meal_day in event_values:
        total += get_agg_day(meal_day, agg_field)
    return total


class AggLib:
    def agg_meal_items_sum(self, meal_items, agg_field):
        return get_agg_meal_items(meal_items, agg_field)

    def agg_meal_day_sum(self, meal_days, agg_field):
        return get_agg_day(meal_days, agg_field)

    def agg_recipe_sum(self, meal_days, agg_field):
        return get_agg_recipe(meal_days, agg_field)

    def agg_meal_event_sum(self, meal_days, agg_field):
        return get_agg_meal_event(meal_days, agg_field)

    def agg_meal_sum(self, meals, agg_field):
        return get_agg_meal(meals, agg_field)

    def agg_day_factors(self, meal_days):
        total = 0
        meals = meal_days.get("meals")
        for meal in meals:
            total += meal.get("day_part_factor")
        return total
    
    def agg_meal_event_energy_kj(self, meal_event):
        total = 0
        meal_days = meal_event.get("meal_days")
        for meal_day in meal_days:
            total += meal_day.get("max_day_part_factor")
        return round(11595.15 * total, 2)
