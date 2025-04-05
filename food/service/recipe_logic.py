from food import models as food_models
from django.db.models import Sum


class RecipeModule:

    def _get_nutri_items(self):
        return ['energy_kj', 'sugar_g', 'fibre_g', 'protein_g', 'sodium_mg','salt_g', 'fat_sat_g']

    def recalculate_recipe_items(self, recipe):

        recipe_item_set = food_models.RecipeItem.objects.filter(
            recipe=recipe)

        recipe_weight_g = recipe_item_set.aggregate(
            sum=Sum('weight_g'))['sum'] or 0

        for recipe_item in recipe_item_set:
            weight_recipe_factor = round(
                recipe_item.weight_g / recipe_weight_g, 3)
            nutri_points = round(
                recipe_item.portion.ingredient.nutri_points * weight_recipe_factor, 1)
            nutri_class = NutriClass.get_nutri_class(
                'solid', recipe_item.portion.ingredient.nutri_points)

            for nutri_item in self._get_nutri_items():
                temp_nutri_value = recipe_item.portion.ingredient._meta.get_field(f"nutri_points_{nutri_item}").value_from_object(recipe_item.portion.ingredient)
                setattr(recipe_item, f"nutri_points_{nutri_item}", round(
                    temp_nutri_value * weight_recipe_factor, 1))

            food_models.RecipeItem.objects.filter(
                id=recipe_item.id).update(
                    nutri_class=nutri_class,
                    nutri_points=nutri_points,
                    weight_recipe_factor=weight_recipe_factor,
                    nutri_points_energy_kj=recipe_item.nutri_points_energy_kj,
                    nutri_points_protein_g=recipe_item.nutri_points_protein_g,
                    nutri_points_fat_sat_g=recipe_item.nutri_points_fat_sat_g,
                    nutri_points_sugar_g=recipe_item.nutri_points_sugar_g,
                    nutri_points_sodium_mg=recipe_item.nutri_points_sodium_mg,
                    nutri_points_fibre_g=recipe_item.nutri_points_fibre_g,
                    nutri_points_fruit_factor=recipe_item.nutri_points_fruit_factor,
                )

    def update_recipe_item_nutritons(self, instance):
        instance.weight_g = round(
            instance.portion.weight_g * instance.quantity, 2)
        instance.energy_kj = round(
            instance.portion.energy_kj * instance.quantity, 2)
        instance.protein_g = round(
            instance.portion.protein_g * instance.quantity, 2)
        instance.fat_g = round(instance.portion.fat_g * instance.quantity, 2)
        instance.fat_sat_g = round(
            instance.portion.fat_sat_g * instance.quantity, 2)
        instance.sugar_g = round(
            instance.portion.sugar_g * instance.quantity, 2)
        instance.sodium_mg = round(
            instance.portion.sodium_mg * instance.quantity, 2)
        instance.carbohydrate_g = round(
            instance.portion.carbohydrate_g * instance.quantity, 2)
        instance.fibre_g = round(
            instance.portion.fibre_g * instance.quantity, 2)

    def get_sum(self, name, items, round_digit=0):
        if (items[f'{name}__sum']):
            return round(items[f'{name}__sum'], round_digit)
        return 0.1

    def recipe_sums(self, instance):
        items = food_models.RecipeItem.objects.filter(recipe=instance.id).aggregate(
            Sum('weight_g'),
            Sum('energy_kj'),
            Sum('protein_g'),
            Sum('fat_g'),
            Sum('fat_sat_g'),
            Sum('sugar_g'),
            Sum('sodium_mg'),
            Sum('carbohydrate_g'),
            Sum('fibre_g'),
        )

        weight_g = self.get_sum('weight_g', items)
        energy_kj = self.get_sum('energy_kj', items)
        protein_g = self.get_sum('protein_g', items)
        fat_g = self.get_sum('fat_g', items)
        fat_sat_g = self.get_sum(
            'fat_sat_g', items)
        sugar_g = self.get_sum('sugar_g', items)
        sodium_mg = self.get_sum('sodium_mg', items)
        carbohydrate_g = self.get_sum('carbohydrate_g', items)
        fibre_g = self.get_sum('fibre_g', items)

        food_models.Recipe.objects.filter(id=instance.id).update(
            weight_g=weight_g,
            energy_kj=energy_kj,
            protein_g=protein_g,
            fat_g=fat_g,
            fat_sat_g=fat_sat_g,
            sugar_g=sugar_g,
            sodium_mg=sodium_mg,
            carbohydrate_g=carbohydrate_g,
            fibre_g=fibre_g)

    def recipe_nutri(self, instance):
        NutriClass = Nutri()
        items = food_models.RecipeItem.objects.filter(recipe=instance.id).aggregate(
            Sum('nutri_points'),
        )

        nutri_points = self.get_sum('nutri_points', items)
        nutri_class = NutriClass.get_nutri_class(
            'solid', nutri_points)

        food_models.Recipe.objects.filter(id=instance.id).update(
            nutri_points=nutri_points,
            nutri_class=nutri_class)
