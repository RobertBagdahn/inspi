from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Price, MetaInfo, Ingredient, Portion, Recipe, RecipeItem

def calculate_recipe_price(recipe):
    print("calculate_recipe_price")
    recipe_items = RecipeItem.objects.filter(recipe=recipe)
    meta_info = MetaInfo.objects.filter(id=recipe.meta_info.id).first()
    price = 0
    for recipe_item in recipe_items:
        price += recipe_item.meta_info.price_eur
    meta_info.price_eur = price
    meta_info.save()

def calculate_recipe_values(recipe):
    print("calculate_recipe_values")
    recipe_items = RecipeItem.objects.filter(recipe=recipe)
    meta_info = MetaInfo.objects.filter(id=recipe.meta_info.id).first()
    weight_g = 0
    for recipe_item in recipe_items:
        weight_g += recipe_item.meta_info.weight_g
    meta_info.weight_g = weight_g
    meta_info.save()

@receiver(post_save, sender=Price)
def create_customer_profile(sender, instance, created, **kwargs):
    ingredient = Ingredient.objects.get(id=instance.portion.ingredient.id)

    # update all meta_info for this ingredient
    meta_info = MetaInfo.objects.filter(id=ingredient.meta_info.id)
    meta_info.update(price_per_kg=instance.price_per_kg)

    meta_infos = MetaInfo.objects.filter(id__in=Portion.objects.filter(ingredient=ingredient).values_list('meta_info', flat=True))
    meta_infos.update(price_per_kg=instance.price_per_kg)
    # update price_per_kg with meta_info weight_g per portion
    for meta_info in meta_infos:
        meta_info.price_eur = meta_info.price_per_kg * (meta_info.weight_g / 1000)
        meta_info.save()

    meta_infos = MetaInfo.objects.filter(id__in=RecipeItem.objects.filter(portion__ingredient=ingredient).values_list('meta_info', flat=True))
    meta_infos.update(price_per_kg=instance.price_per_kg)

    for meta_info in meta_infos:
        meta_info.price_eur = meta_info.price_per_kg * (meta_info.weight_g / 1000)
        meta_info.save()

    # add all recipe items prices to recipe price
    recipes = Recipe.objects.filter(id__in=RecipeItem.objects.filter(portion__ingredient=ingredient).values_list('recipe', flat=True))

    for recipe in recipes:
        calculate_recipe_price(recipe)


@receiver(post_save, sender=RecipeItem)
def create_customer_profile(sender, instance, created, **kwargs):
    # set the price for recipe item
    meta_info_ingredient = MetaInfo.objects.get(id=instance.portion.ingredient.meta_info.id)
    meta_info = MetaInfo.objects.get(id=instance.meta_info.id)
    meta_info.weight_g = instance.quantity * instance.portion.meta_info.weight_g
    meta_info.price_per_kg = meta_info_ingredient.price_per_kg
    meta_info.price_eur = instance.portion.meta_info.price_per_kg * (instance.quantity * instance.portion.meta_info.weight_g / 1000)

    print(instance.portion.meta_info.price_per_kg * (instance.quantity * instance.portion.meta_info.weight_g / 1000))
    print(instance.portion.meta_info.price_per_kg)
    print(instance.quantity)
    print(instance.portion.meta_info.weight_g)

    meta_info.save()

    calculate_recipe_price(instance.recipe)
    calculate_recipe_values(instance.recipe)
    print("RecipeItem created")
