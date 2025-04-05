from food import models as food_models
import logging


logger = logging.getLogger(__name__)


def add_hints(recipe, parameter, recipe_objective=None):
    hints: food_models.RecipeHint = food_models.RecipeHint.objects.all()

    matching_hints = []
    for hint in hints:
        if hint.parameter == parameter:
            recipe_value = getattr(recipe.meta_info, parameter, -1)
            check_value = hint.value

            # Check if recipe_type and recipe_objective match or are not specified
            type_matches = (
                not hint.recipe_type or hint.recipe_type == recipe.recipe_type
            )
            objective_matches = (
                not recipe_objective or hint.recipe_objective == recipe_objective
            )

            if (
                (
                    (hint.min_max == "max" and check_value < recipe_value)
                    or (hint.min_max == "min" and check_value >= recipe_value)
                )
                and type_matches
                and objective_matches
            ):
                matching_hints.append(hint)

    return matching_hints
