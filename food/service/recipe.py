# import models
from food.models import Recipe, RecipeItem


def update_recipe(recipe):
    """
    Update a recipe.
    """

    fields = [
        "energy_kj",
        "protein_g",
        "fat_g",
        "fat_sat_g",
        "sugar_g",
        "sodium_mg",
        "salt_g",
        "fruit_factor",
        "carbohydrate_g",
        "fibre_g",
        "fructose_g",
        "lactose_g",
    ]

    # update meta info for all recipe items based on ingredients
    recipe_items = RecipeItem.objects.filter(recipe=recipe)
    # update recipe_items meta info
    for item in recipe_items:
        for field in fields:
            setattr(
                item.meta_info,
                field,
                getattr(item.portion.ingredient.meta_info, field, 0)
                * 0.01
                * item.quantity
                * item.portion.meta_info.weight_g,
            )
        item.meta_info.save()

    # update recipe meta info
    for field in fields:
        setattr(
            recipe.meta_info,
            field,
            sum(getattr(item.meta_info, field, 0) for item in recipe_items),
        )
    recipe.meta_info.save()
