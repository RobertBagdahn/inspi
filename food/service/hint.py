from food import models as food_models


class HintModule:
    def add_hints(self, recipe):
        hints: food_models.Hint = food_models.Hint.objects.all()

        recipe.hints.clear()

        for hint in hints:
            recipe_value = recipe._meta.get_field(
                hint.parameter).value_from_object(recipe)

            if not recipe_value:
                recipe_value = 0
            check_value = hint.value

            if (hint.min_max == 'max' and check_value < recipe_value) or (
                    hint.min_max == 'min' and check_value >= recipe_value):
                recipe.hints.add(hint)

        return True
