# import models
from food.models import Recipe, RecipeItem
from food.service.nutri_lib import get_nutri_class

# import from food/service/nutri_lib.py



def update_recipe(recipe):
    """
    Update a recipe.
    """

    sum_fields = [
        "energy_kj",
        "protein_g",
        "fat_sat_g",
        "sugar_g",
        "sodium_mg",
        "fibre_g",
    ]

    mean_fields = [
        "fruit_factor",
        "price_per_kg",
    ]


    # update meta info for all recipe items based on ingredients
    recipe_items = RecipeItem.objects.filter(recipe=recipe)
    # update recipe_items meta info
    for item in recipe_items:
        for field in sum_fields:
            if hasattr(item, 'portion') and item.portion and hasattr(item.portion, 'ingredient') and item.portion.ingredient:
                setattr(
                    item.meta_info,
                    field,
                    getattr(item.portion.ingredient.meta_info, field, 0)
                    * item.quantity * item.portion.meta_info.weight_g / 100
                )
                # Update nutri_points from ingredient meta_info
                if hasattr(item.portion, 'ingredient') and item.portion.ingredient and hasattr(item.portion.ingredient.meta_info, 'nutri_points'):
                    # Update nutri_points based on key nutritional fields
                    item_nutri_points = 0
                    if hasattr(item.portion.ingredient.meta_info, field):
                        field_string = f"nutri_points_{field}"
                        
                        nutri_points = getattr(item.portion.ingredient.meta_info, field_string, 0)
                        setattr(item.meta_info, field_string, nutri_points)
                        item_nutri_points += nutri_points
                    item.meta_info.nutri_points = round(item_nutri_points, 1)
                    # Update fruit_factor from ingredient meta_info
                    if hasattr(item.portion.ingredient.meta_info, 'fruit_factor'):
                        item.meta_info.fruit_factor = item.portion.ingredient.meta_info.fruit_factor

                    # Also update nutri_class if available
                    if hasattr(item.portion.ingredient.meta_info, 'nutri_class'):
                        item.meta_info.nutri_class = item.portion.ingredient.meta_info.nutri_class

                item.meta_info.save()

            elif hasattr(item, 'sub_recipe') and item.sub_recipe:
                setattr(
                    item.meta_info,
                    field,
                    getattr(item.sub_recipe.meta_info, field, 0)
                    * item.quantity
                )
            

        if hasattr(item, 'sub_recipe') and item.sub_recipe and item.sub_recipe.meta_info:
            item.meta_info.weight_g = item.quantity * item.sub_recipe.meta_info.weight_g
            item.meta_info.price_per_kg = item.sub_recipe.meta_info.price_per_kg
            item.meta_info.price_eur = round(item.quantity * item.sub_recipe.meta_info.price_eur, 2)
            item.meta_info.nutri_points = item.sub_recipe.meta_info.nutri_points
            item.meta_info.nutri_class = item.sub_recipe.meta_info.nutri_class
            item.meta_info.fruit_factor = item.sub_recipe.meta_info.fruit_factor

            item.meta_info.save()

    # update recipe meta info
    for field in sum_fields + ['weight_g', 'price_eur']:
        setattr(
            recipe.meta_info,
            field,
            sum(getattr(item.meta_info, field, 0) for item in recipe_items),
        )
        # Set field_string for each nutritional field
        field_string = f"nutri_points_{field}"
        setattr(
            recipe.meta_info,
            field_string,
            sum(getattr(item.meta_info, field_string, 0) for item in recipe_items),
        )

        # nutri_class from get_nutri_class
        recipe.meta_info.nutri_class = get_nutri_class('solid', recipe.meta_info.nutri_points)




    recipe.meta_info.save()
