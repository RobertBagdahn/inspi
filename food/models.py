import datetime

from django.db import models
from django.db.models import Sum, Count
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator

from .choices import (
    SuitLevel,
    WarmMeal,
    MealTimeOptions,
    ChildFrendly,
    PhysicalViscosityChoices,
    Units,
    BrandQualityChoises,
    RetailerTypeChoise,
    PhysicalActivityLevelChoise,
    MealType,
    RecipeType,
    RecipeStatus,
    IngredientStatus,
    HintLevel,
    MinMaxLevel,
    ParameterChoice,
    RecipeObjective,
)

from general.login.models import CustomUser
from group.models import InspiGroup
from django.core.exceptions import ValidationError
import uuid


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class MeasuringUnit(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.FloatField()
    unit = models.CharField(
        max_length=2,
        choices=Units.choices,
        default=Units.MASS,
    )

    def __str__(self):
        return f"{self.name} - {self.description}"

    def __repr__(self):
        return self.__str__()


class NutritionalTag(TimeStampMixin):
    name = models.CharField(
        max_length=255,
        help_text="Name of the tag. E.g. 'Fleisch', 'Alkohol', 'Nüsse', Scharf",
    )
    name_opposite = models.CharField(
        max_length=255,
        help_text="Name of the tag for human readable output. e.g. 'Vegan', 'Vegetarisch', 'Alkoholfrei'",
    )
    description = models.CharField(max_length=255)
    description_human = models.CharField(max_length=255)
    rank = models.IntegerField(default=1)
    is_dangerous = models.BooleanField(
        default=False,
        help_text="Indicates if this tag represents a potentially harmful or dangerous ingredient",
    )
    default_in_event = models.BooleanField(
        default=False,
        help_text="Indicates if this tag is automatically included in the event",
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class MetaInfo(TimeStampMixin):
    energy_kj = models.FloatField(default=0, blank=True, null=True)
    protein_g = models.FloatField(default=0, blank=True, null=True)
    fat_g = models.FloatField(default=0, blank=True, null=True)
    fat_sat_g = models.FloatField(default=0, blank=True, null=True)
    sugar_g = models.FloatField(default=0, blank=True, null=True)
    sodium_mg = models.FloatField(default=0, blank=True, null=True)
    salt_g = models.FloatField(default=0, blank=True, null=True)
    fruit_factor = models.FloatField(default=0, blank=True, null=True)
    carbohydrate_g = models.FloatField(default=0, blank=True, null=True)
    fibre_g = models.FloatField(default=0, blank=True, null=True)
    fructose_g = models.FloatField(default=0, blank=True, null=True)
    lactose_g = models.FloatField(default=0, blank=True, null=True)

    nutri_points_energy_kj = models.FloatField(default=0)
    nutri_points_protein_g = models.FloatField(default=0)
    nutri_points_fat_sat_g = models.FloatField(default=0)
    nutri_points_sugar_g = models.FloatField(default=0)
    nutri_points_sodium_mg = models.FloatField(default=0)
    nutri_points_fibre_g = models.FloatField(default=0)
    nutri_points_fruit_factor = models.FloatField(default=0)

    nutri_points = models.FloatField(blank=True, null=True)
    nutri_class = models.FloatField(null=True, blank=True)

    price_per_kg = models.FloatField(default=0.00, blank=True, null=True)
    price_eur = models.FloatField(default=0.00, blank=True, null=True)

    weight_g = models.FloatField(default=0, blank=True, null=True)
    volume_ml = models.FloatField(default=0, blank=True, null=True)

    @property
    def weight_display(self):
        if self.weight_g > 1000:
            return f"{round(self.weight_g/1000,1)} kg"
        return f"{round(self.weight_g, 0)} g"

    @property
    def nutri_score_display(self):
        return {1: "A", 2: "B", 3: "C", 4: "D", 5: "E"}.get(self.nutri_class, "Unknown")

    def __str__(self):
        return f"MetaInfo {self.id}" if self.id else "MetaInfo"

    def __repr__(self):
        return self.__str__()


class RetailSection(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Ingredient(TimeStampMixin):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    physical_density = models.FloatField(default=1)
    physical_viscosity = models.CharField(
        max_length=10,
        choices=PhysicalViscosityChoices.choices,
        default=PhysicalViscosityChoices.SOLID,
    )
    durability_in_days = models.IntegerField(
        default=0,
        help_text="Durability in days. 0 = unknown, 1-365 = days, >365 = years",
        blank=True,
        null=True,
    )
    max_storage_temperature = models.IntegerField(
        default=20,
        help_text="",
        blank=True,
        null=True,
    )
    nova_score = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    standard_recipe_weight_g = models.FloatField(
        default=100,
        help_text="Default weight in grams used in a standard recipe",
        blank=True,
        null=True,
    )
    ingredient_ref = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True
    )
    fdc_id = models.IntegerField(null=True, blank=True)
    nan_art_id_rewe = models.IntegerField(null=True, blank=True)
    ean = models.BigIntegerField(null=True, blank=True)

    retail_section = models.ForeignKey(
        RetailSection, on_delete=models.PROTECT, null=True, blank=True
    )
    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )
    nutritional_tags = models.ManyToManyField(NutritionalTag, blank=True)
    child_frendly_score = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    scout_frendly_score = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    environmental_influence_score = models.IntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, null=True, blank=True
    )
    status = models.CharField(
        max_length=11, choices=IngredientStatus.choices, default=IngredientStatus.DRAFT
    )
    recipe_counts = models.IntegerField(
        help_text="Number of recipes using this ingredient",
        default=0,
    )
    is_unprepaired_consumable = models.BooleanField(
        default=False,
        help_text="Indicates if this ingredient is as snack consumable without preparation",
    )
    managed_by = models.ManyToManyField(
        CustomUser,
        related_name="ingredients_managed",
        blank=True,
        default=None,
    )
    managed_by_group = models.ManyToManyField(
        InspiGroup,
        related_name="ingredients_managed_group",
        blank=True,
        help_text="Groups that manage this ingredient",
        default=None,
    )

    @property
    def nan_rewe(self):
        try:
            return self.nan_art_id_rewe - 100000000
        except TypeError:
            return False

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()


class IngredientAlias(TimeStampMixin):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="aliases"
    )
    name = models.CharField(
        max_length=100, help_text="Alternative name for the ingredient"
    )
    rank = models.IntegerField(default=1)
    created_by = models.ForeignKey(CustomUser, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Ingredient aliases"
        ordering = ["-rank", "name"]
        unique_together = ["ingredient", "rank"]
        constraints = [
            models.UniqueConstraint(
                fields=["rank", "ingredient"], name="unique_ingredient_alias_rank"
            )
        ]

    def __str__(self):
        return f"{self.name} → {self.ingredient.name}"


class Portion(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True, null=True)
    measuring_unit = models.ForeignKey(
        MeasuringUnit, on_delete=models.PROTECT, blank=True, null=True, default=3
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, default=1, related_name="portions"
    )
    quantity = models.FloatField(default=1)
    rank = models.IntegerField(default=1)
    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} / {self.quantity} {self.measuring_unit} / {self.ingredient.name}"

    def __repr__(self):
        return self.__str__()

    @property
    def price_eur(self):
        if self.meta_info.weight_g and self.meta_info.price_per_kg:
            return self.meta_info.weight_g * self.meta_info.price_per_kg * 1000
        return 0.00

    @property
    def prices(self):
        return Price.objects.filter(portion=self).order_by("price_eur")

    class Meta:
        ordering = ("name",)


class RecipeHint(TimeStampMixin):
    hint = models.CharField(max_length=50, blank=True)
    improvement = models.CharField(max_length=1000, blank=True)
    value = models.FloatField(default=1)
    hint_level = models.CharField(
        max_length=10,
        choices=HintLevel.choices,
        default=HintLevel.INFO,
    )
    min_max = models.CharField(
        max_length=10,
        choices=MinMaxLevel.choices,
        default=MinMaxLevel.MIN,
    )
    parameter = models.CharField(
        max_length=23,
        choices=ParameterChoice.choices,
        default=ParameterChoice.weight_g,
    )
    recipe_type = models.CharField(
        max_length=11,
        choices=RecipeType.choices,
        default=RecipeType.WARN_LUNCH,
        blank=True,
        null=True,
        help_text="Recipe type this hint applies to (if specific)",
    )
    recipe_objective = models.CharField(
        max_length=20,
        choices=RecipeObjective.choices,
        default=RecipeObjective.health,
        blank=True,
        null=True,
        help_text="Recipe objective this hint applies to (if specific)",
    )

    def __str__(self):
        return f"{self.hint} - {self.value}"

    def __repr__(self):
        return super().__repr__()


class Recipe(TimeStampMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    recipe_type = models.CharField(
        max_length=11, choices=RecipeType.choices, default=RecipeType.WARN_LUNCH
    )
    status = models.CharField(
        max_length=11, choices=RecipeStatus.choices, default=RecipeStatus.SIMULATOR
    )
    hints = models.ManyToManyField(RecipeHint, blank=True)
    managed_by = models.ManyToManyField(
        CustomUser, related_name="recipe_created_by", blank=True
    )
    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, null=True, blank=True
    )
    recipe_ref = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Reference to the orgignal recipe if this is a modified version",
    )

    @property
    def is_public(self):
        """
        Determines if a recipe can be viewed based on status
        Public recipes can always be viewed
        """

        is_public = self.status in [RecipeStatus.PUBLIC, RecipeStatus.APPROVED]

        return is_public
    
    @property
    def get_update_url(self):
        """
        Returns the URL for updating this recipe
        """
        return f"/food/recipe/{self.slug}/update" if self.slug else None

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()


class RecipeItem(TimeStampMixin):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="recipe_items",
    )
    portion = models.ForeignKey(
        Portion,
        on_delete=models.PROTECT,
        related_name="recipe_items",
        blank=True,
        null=True,
    )
    sub_recipe = models.ForeignKey(
        Recipe,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="used_in_recipes",
    )
    quantity = models.FloatField(default=1)

    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )

    def clean(self):
        # Ensure that exactly one of portion or sub_recipe is provided
        if (self.portion is None and self.sub_recipe is None) or (
            self.portion is not None and self.sub_recipe is not None
        ):
            raise ValidationError(
                "Either portion OR sub_recipe must be provided, not both or neither."
            )

    @property
    def weight_quote(self):
        return round(
            float(self.meta_info.weight_g)
            / float(self.recipe.meta_info.weight_g)
            * 100.0,
            2,
        )

    @property
    def weighted_nutri_points_energy_kj(self):
        return self.meta_info.nutri_points_energy_kj * self.weight_quote / 100

    @property
    def weighted_nutri_points_protein_g(self):
        return self.meta_info.nutri_points_protein_g * self.weight_quote / 100

    @property
    def weighted_nutri_points_fat_sat_g(self):
        return self.meta_info.nutri_points_fat_sat_g * self.weight_quote / 100

    @property
    def weighted_nutri_points_sugar_g(self):
        return self.meta_info.nutri_points_sugar_g * self.weight_quote / 100

    @property
    def weighted_nutri_points_sodium_mg(self):
        return self.meta_info.nutri_points_sodium_mg * self.weight_quote / 100

    @property
    def weighted_nutri_points_fibre_g(self):
        return self.meta_info.nutri_points_fibre_g * self.weight_quote / 100
    
    @property
    def weighted_nutri_points_fruit_factor(self):
        return self.meta_info.nutri_points_fruit_factor * self.weight_quote / 100
    
    @property
    def weighted_nutri_points(self):
        return self.meta_info.nutri_points * self.weight_quote / 100

    def __str__(self):
        return f"{self.recipe} - {self.quantity} x {self.portion}"

    def __repr__(self):
        return self.__str__()


@receiver(post_save, sender=RecipeItem)
def update_ingredient_recipe_count(sender, instance, **kwargs):
    """Update recipe_counts for each ingredient when a RecipeItem is saved"""
    if instance.portion and instance.portion.ingredient:
        # Get the ingredient
        ingredient = instance.portion.ingredient
        # Count unique recipes using this ingredient
        recipe_count = (
            RecipeItem.objects.filter(portion__ingredient=ingredient)
            .values("recipe")
            .distinct()
            .count()
        )
        # Update the count
        ingredient.recipe_counts = recipe_count
        ingredient.save()


@receiver(models.signals.post_delete, sender=RecipeItem)
def update_ingredient_recipe_count_on_delete(sender, instance, **kwargs):
    """Update recipe_counts when a RecipeItem is deleted"""
    if instance.portion and instance.portion.ingredient:
        # Get the ingredient
        ingredient = instance.portion.ingredient
        # Count unique recipes using this ingredient
        recipe_count = (
            RecipeItem.objects.filter(portion__ingredient=ingredient)
            .values("recipe")
            .distinct()
            .count()
        )
        # Update the count
        ingredient.recipe_counts = recipe_count
        ingredient.save()


class Price(TimeStampMixin):
    price_eur = models.FloatField()
    name = models.CharField(max_length=255, blank=True)
    portion = models.ForeignKey(
        Portion, on_delete=models.PROTECT, null=True, blank=True
    )
    quantity = models.FloatField(default=0)
    retailer = models.CharField(
        max_length=255,
        choices=RetailerTypeChoise.choices,
        default=RetailerTypeChoise.SUPERMARKET,
    )
    quality = models.CharField(
        max_length=10,
        choices=BrandQualityChoises.choices,
        default=BrandQualityChoises.BRAND,
    )

    @property
    def price_per_kg(self):
        return round(
            float(self.price_eur)
            / float(
                float(self.portion.meta_info.weight_g) * float(self.quantity) / 1000
            ),
            2,
        )

    @property
    def weight_g(self):
        return float(self.portion.meta_info.weight_g) * float(self.quantity)

    def __str__(self):
        return f"{self.price_eur} € - {self.retailer}"

    def __repr__(self):
        return self.__str__()


class TemplateOption(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class MealEventTemplate(TimeStampMixin):
    name = models.CharField(max_length=255, default="Unbekannt")
    description = models.CharField(max_length=255, blank=True, null=True)
    max_price_eur = models.FloatField(default=5.99)
    is_public = models.BooleanField(default=False)
    suit_level = models.CharField(
        max_length=10,
        choices=SuitLevel.choices,
        default=SuitLevel.Medium,
    )
    warm_meal = models.CharField(
        max_length=10,
        choices=WarmMeal.choices,
        default=WarmMeal.JustEvening,
    )
    meal_time_options = models.CharField(
        max_length=10,
        choices=MealTimeOptions.choices,
        default=MealTimeOptions.SIMPLE_WEEKEND,
    )
    child_frendly = models.CharField(
        max_length=10,
        choices=ChildFrendly.choices,
        default=ChildFrendly.CHILD_AND_ADULT,
    )
    nutritional_tags = models.ManyToManyField(NutritionalTag, blank=True)
    template_options = models.ManyToManyField(TemplateOption, blank=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, null=True, blank=True
    )


class MealEvent(TimeStampMixin):
    event_name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=False, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    norm_portions = models.IntegerField()
    activity_factor = models.CharField(
        max_length=10,
        choices=PhysicalActivityLevelChoise.choices,
        default=PhysicalActivityLevelChoise.Zeltlager,
    )
    meal_event_ref = models.ForeignKey(
        "self", on_delete=models.PROTECT, null=True, blank=True
    )
    meal_event_template = models.ForeignKey(
        MealEventTemplate, on_delete=models.PROTECT, null=True, blank=True
    )
    reserve_factor = models.FloatField(default=1.0)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )
    managed_by = models.ManyToManyField(
        CustomUser, related_name="meal_event_created_by", blank=True
    )

    def __str__(self):
        return f"{self.event_name} - {self.norm_portions} Personen"

    def __repr__(self):
        return self.__str__()

    def list_meal_days(self):
        return MealDay.objects.filter(meal_event=self).order_by("date")

    def list_meals(self):
        # filter all meals with with connected meal_days in meal_event=self
        return Meal.objects.filter(meal_day__meal_event=self)


class MealDay(TimeStampMixin):
    meal_event = models.ForeignKey(MealEvent, on_delete=models.CASCADE, null=True)
    max_day_part_factor = models.FloatField(default=1)
    date = models.DateField(default=datetime.date.today, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.meal_event}"

    def __repr__(self):
        return self.__str__()

    def list_meals(self):
        return self.meal_set.all().order_by("time_start")


class Meal(TimeStampMixin):
    name = models.CharField(default="Hauptessen", max_length=255, null=True, blank=True)
    meal_day = models.ForeignKey(MealDay, on_delete=models.CASCADE, null=True)
    day_part_factor = models.FloatField(default=0.33)
    meal_type = models.CharField(
        max_length=10, choices=MealType.choices, default=MealType.WARN_MEAL
    )
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    is_public = models.BooleanField(default=False)

    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.name} - {self.meal_day.meal_event.event_name}"

    def __repr__(self):
        return self.__str__()

    def list_meal_items(self):
        return self.mealitem_set.all().order_by("recipe__name")


class MealItem(TimeStampMixin):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    factor = models.FloatField(default=1)
    meta_info = models.ForeignKey(
        MetaInfo, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.recipe.name} - {self.meal.name}"

    def __repr__(self):
        return self.__str__()


# pylint: disable=unused-argument
@receiver(pre_save, sender=Ingredient)
def save_recipe(sender, instance: Ingredient, **kwargs):
    pass
    # import requests
    # import json

    # if instance.fdc_id and not instance.energy_kj:
    #     API_URL = "https://api.nal.usda.gov/fdc/v1/food"
    #     API_KEY = "?api_key=wrSx9QbtEeaZb3LHWXzm4egDf2uiBPdOEmGsc9tT"

    #     response = requests.get(f"{API_URL}/{instance.fdc_id}/{API_KEY}")
    #     if response.text is None or response.text == '':
    #         print(f'Error in fetching data from National Agricultural Library')
    #         print(f'received: {response.text=}')
    #         print(f'Error: {response.status_code}: {response.content}')
    #         print(f'reason: {response.reason}')
    #         print(f'url: {API_URL}/{instance.fdc_id}/{API_KEY}')
    #         return

    #     dict_data = json.loads(response.text)

    #     if 'foodNutrients' in dict_data:
    #         nutri_list = dict_data['foodNutrients']
    #         instance.energy_kj = 0
    #         instance.protein_g = 0
    #         instance.fat_sat_g = 0
    #         instance.fat_g = 0
    #         instance.sugar_g = 0
    #         instance.sodium_mg = 0
    #         instance.carbohydrate_g = 0
    #         instance.fibre_g = 0
    #         if 'ndbNumber' in dict_data:
    #             instance.ndb_number = dict_data['ndbNumber']

    #         if 'foodCategory' in dict_data:
    #             instance.major_class = dict_data['foodCategory']['description']

    #         for item in nutri_list:
    #             if item['type'] == 'FoodNutrient':
    #                 nutrient = item['nutrient']

    #                 if (nutrient['id'] == 2047):
    #                     instance.energy_kj = round(
    #                         int(item['amount']) * 4.1, 0)
    #                 elif (nutrient['id'] == 1008):
    #                     instance.energy_kj = round(
    #                         int(item['amount']) * 4.1, 0)

    #                 if (nutrient['id'] == 1003):
    #                     instance.protein_g = item['amount']

    #                 if (nutrient['id'] == 1258):
    #                     instance.fat_sat_g = item['amount']

    #                 if (nutrient['id'] == 2000):
    #                     instance.sugar_g = item['amount']

    #                 if (nutrient['id'] == 1004):
    #                     instance.fat_g = item['amount']

    #                 if (nutrient['id'] == 1093):
    #                     instance.sodium_mg = item['amount']
    #                     instance.salt_g = item['amount'] * 2.5 / 1000

    #                 if (nutrient['id'] == 1005):
    #                     instance.carbohydrate_g = item['amount']

    #                 if (nutrient['id'] == 1079):
    #                     instance.fibre_g = item['amount']

    #                 if (nutrient['id'] == 1012):
    #                     instance.fructose_g = item['amount']

    #                 if (nutrient['id'] == 1013):
    #                     instance.lactose_g = item['amount']


# pylint: disable=unused-argument
# @receiver(post_save, sender=Ingredient)
# def post_save_recipe(sender, instance, created, **kwargs):
#     if not getattr(instance, "processed", False):
#         NutriClass = Nutri()
#         physical_viscosity = instance.physical_viscosity
#         nutri_items = NutriClass.get_nutri_items()
#         nutri_points = 0
#         for item in nutri_items:
#             value = instance._meta.get_field(item).value_from_object(instance)
#             temp_points = NutriClass.get_points(item, physical_viscosity, value)
#             setattr(instance, f"nutri_points_{item}", temp_points)
#             nutri_points = temp_points + nutri_points

#         instance.nutri_points = nutri_points
#         instance.nutri_class = NutriClass.get_nutri_class(
#             "solid", instance.nutri_points
#         )
#         instance.processed = True
#         instance.save()

#         if created:
#             Portion.objects.create(ingredient=instance, name=f"{instance.name} in g")
