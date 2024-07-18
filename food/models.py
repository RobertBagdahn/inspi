import datetime

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from food.service.nutri_lib import Nutri
from food.service.recipe_logic import RecipeModule
from food.service.hint import HintModule
from food.service.price_logic import PriceModule

User = get_user_model()


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class FoodMajorClasses(models.TextChoices):
    BACKED = "Baked Products", "Backwaren"
    BEEF = "Beef Products", "Ringfleisch"
    BEVERRAGES = "Beverages", "Getränk"
    PASTA = "Cereal Grains and Pasta", "Nudeln und Getreide "
    EGG = "Dairy and Egg Products", "Milch und Ei"
    FATS = "Fats and Oils", "Fette und and Öl"
    FISH = "Finfish and Shellfish Products", "Meeresfrücht und Fisch"
    FRUIT = "Fruits and Fruit Juices", "Früchte"
    LEGUNE = "Legumes and Legume Products", "Hülsenfrüchte"
    NUTS = "Nut and Seed Products", "Nuß und Samen"
    PORK = "Pork Products", "Schweinefleisch"
    POULTRY = "Poultry Products", "Geflügel"
    SAUSAGES = "Sausages and Luncheon Meats", "Wurst"
    SOUPS = "Soups, Sauces, and Gravies", "Suppe oder Soße"
    SPICES = "Spices and Herbs", "Gewürz"
    SWEETS = "Sweets", "Süßigkeit"
    VEGETABLES = "Vegetables and Vegetable Products", "Gemüse"
    UNDEFINED = "undefined", "unbekannt"


class NutrientsMixin(models.Model):
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

    class Meta:
        abstract = True


class NutriPointsMixin(models.Model):
    nutri_points_energy_kj = models.FloatField(default=0)
    nutri_points_protein_g = models.FloatField(default=0)
    nutri_points_fat_sat_g = models.FloatField(default=0)
    nutri_points_sugar_g = models.FloatField(default=0)
    nutri_points_salt_g = models.FloatField(default=0)
    nutri_points_sodium_mg = models.FloatField(default=0)
    nutri_points_fibre_g = models.FloatField(default=0)

    class Meta:
        abstract = True


class MeasuringUnit(TimeStampMixin):
    class Units(models.TextChoices):
        VOLUME = "ml", "Millilitter"
        MASS = "g", "Gramm"

    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    quantity = models.FloatField()
    unit = models.CharField(
        max_length=2,
        choices=Units.choices,
        default=Units.MASS,
    )

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class TagCategory(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    is_ingredient = models.BooleanField(default=True)
    is_recipe = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Tag(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    tag_category = models.ForeignKey(TagCategory, on_delete=models.PROTECT, null=True)
    is_ingredient = models.BooleanField(default=True)
    is_recipe = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Ingredient(TimeStampMixin, NutrientsMixin, NutriPointsMixin):
    class PhysicalViscosityChoices(models.TextChoices):
        SOLID = "solid", "Essen"
        BEVERAGE = "beverage", "Getränk"

    name = models.CharField(max_length=40)
    description = models.CharField(max_length=255, blank=True, null=True)
    physical_density = models.FloatField(default=1)
    physical_viscosity = models.CharField(
        max_length=10,
        choices=PhysicalViscosityChoices.choices,
        default=PhysicalViscosityChoices.SOLID,
    )
    tags = models.ManyToManyField(Tag, related_name="IngredientTags", blank=True)
    fdc_id = models.IntegerField(null=True, blank=True)
    major_class = models.CharField(
        max_length=60,
        choices=FoodMajorClasses.choices,
        default=FoodMajorClasses.UNDEFINED,
    )

    # readonly
    nutri_points = models.IntegerField(null=True, blank=True)
    nutri_class = models.FloatField(null=True, blank=True)
    ndb_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.description}"

    def __repr__(self):
        return self.__str__()


class Portion(TimeStampMixin, NutrientsMixin):
    name = models.CharField(max_length=255)
    measuring_unit = models.ForeignKey(
        MeasuringUnit, on_delete=models.PROTECT, blank=True, null=True, default=3
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, default=1)
    quantity = models.FloatField(default=1)
    rank = models.IntegerField(default=1)
    # readonly
    weight_g = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_g = self.measuring_unit.unit == "g"
        if is_g:
            self.weight_g = self.measuring_unit.quantity * self.quantity
        else:
            self.weight_g = (
                self.measuring_unit.quantity
                * self.quantity
                * self.ingredient.physical_density
            )

        # Nutrients
        self.energy_kj = round(self.ingredient.energy_kj * self.weight_g / 100, 2)
        self.protein_g = round(self.ingredient.protein_g * self.weight_g / 100, 2)
        self.fat_g = round(self.ingredient.fat_g * self.weight_g / 100, 2)
        self.fat_sat_g = round(self.ingredient.fat_sat_g * self.weight_g / 100, 2)
        self.sugar_g = round(self.ingredient.sugar_g * self.weight_g / 100, 2)
        self.sodium_mg = round(self.ingredient.sodium_mg * self.weight_g / 100, 2)
        self.carbohydrate_g = round(
            self.ingredient.carbohydrate_g * self.weight_g / 100, 2
        )
        fibre_g = 0
        if self.ingredient.fibre_g:
            fibre_g = self.ingredient.fibre_g
        self.fibre_g = round(fibre_g * self.weight_g / 100, 2)

        super(Portion, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} / {self.quantity} {self.measuring_unit}"

    def __repr__(self):
        return self.__str__()

    class Meta:
        ordering = ("name",)


class Hint(TimeStampMixin):
    class HintLevel(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warn", "Achtung"
        ERROR = "error", "Fehler"

    class MinMaxLevel(models.TextChoices):
        MAX = "max", "Maximal"
        MIN = "min", "Minimal"

    class ParameterChoice(models.TextChoices):
        weight_g = "weight_g", "weight_g"
        energy_kj = "energy_kj", "energy_kj"
        protein_g = "protein_g", "protein_g"
        fat_g = "fat_g", "fat_g"
        fat_sat_g = "fat_sat_g", "fat_sat_g"
        sugar_g = "sugar_g", "sugar_g"
        sodium_mg = "sodium_mg", "sodium_mg"
        salt_g = "salt_g", "salt_g"
        carbohydrate_g = "carbohydrate_g", "carbohydrate_g"
        fibre_g = "fibre_g", "fibre_g"
        nutri_points = "nutri_points", "nutri_points"
        nutri_class = "nutri_class", "nutri_class"

    name = models.CharField(max_length=50, blank=True)
    description = models.CharField(max_length=1000, blank=True)
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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class MealType(models.TextChoices):
    BREAKFAST = "breakfast", "Frühstück"
    LUNCH_WARM = "lunch_warm", "Menu (warm)"
    LUNCH_COLD = "lunch_cold", "Menu (kalt)"
    DESSERT = "dessert", "Nachtisch"
    SNACK = "snack", "Snack"
    DRINK = "drink", "Getränk"


class RecipeStatus(models.TextChoices):
    SIMULATOR = "simulator", "Simulator"
    VERIFIED = "verified", "Verified by Inspi"
    USER_CONENT = "user_conent", "Benutzer erstellt"
    USER_CONENT_PUBLIC = "user_public", "Benutzer Öffentlich"


class Recipe(TimeStampMixin, NutrientsMixin):
    name = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    tags = models.ManyToManyField(Tag, related_name="RecipeTags", blank=True)
    meal_type = models.CharField(
        max_length=11, choices=MealType.choices, default=MealType.LUNCH_WARM
    )
    status = models.CharField(
        max_length=11, choices=RecipeStatus.choices, default=RecipeStatus.SIMULATOR
    )
    # readonly
    nutri_class = models.FloatField(null=True, blank=True)
    nutri_points = models.FloatField(null=True, blank=True)
    weight_g = models.FloatField(default=1)
    hints = models.ManyToManyField(Hint, blank=True)
    created_by = models.ManyToManyField(
        User, related_name="recipe_created_by", blank=True
    )

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        RecipeClass = RecipeModule()
        HintClass = HintModule()

        RecipeClass.recipe_sums(self)
        RecipeClass.recalculate_recipe_items(self)
        RecipeClass.recipe_nutri(self)

        super(Recipe, self).save(*args, **kwargs)

        HintClass.add_hints(self)


class RecipeItem(TimeStampMixin, NutrientsMixin, NutriPointsMixin):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="recipe_items",
    )
    portion = models.ForeignKey(
        Portion, on_delete=models.PROTECT, related_name="recipe_items"
    )
    quantity = models.FloatField(default=1)
    # readonly
    weight_g = models.FloatField(blank=True, null=True)
    weight_recipe_factor = models.FloatField(blank=True, null=True)
    nutri_points = models.FloatField(blank=True, null=True)
    nutri_class = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.recipe} - {self.quantity} x {self.portion}"

    def __repr__(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        RecipeClass = RecipeModule()
        HintClass = HintModule()

        RecipeClass.update_recipe_item_nutritons(self)
        super(RecipeItem, self).save(*args, **kwargs)

        RecipeClass.recipe_sums(self.recipe)
        RecipeClass.recalculate_recipe_items(self.recipe)
        RecipeClass.recipe_nutri(self.recipe)

        HintClass.add_hints(self.recipe)

    def delete(self, *args, **kwargs):
        RecipeClass = RecipeModule()
        HintClass = HintModule()

        RecipeClass.update_recipe_item_nutritons(self)
        super(RecipeItem, self).delete(*args, **kwargs)

        RecipeClass.recipe_sums(self.recipe)
        RecipeClass.recalculate_recipe_items(self.recipe)
        RecipeClass.recipe_nutri(self.recipe)

        HintClass.add_hints(self.recipe)


class Retailer(TimeStampMixin):
    name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


class Package(TimeStampMixin):
    class BrandQualityChoises(models.TextChoices):
        OWN = "own", "Eigenmarke"
        BRAND = "brand", "Marke"
        PREMIUM = "premium", "Premium"

    name = models.CharField(max_length=255, blank=True)
    portion = models.ForeignKey(Portion, on_delete=models.PROTECT, null=True)
    quality = models.CharField(
        max_length=10,
        choices=BrandQualityChoises.choices,
        default=BrandQualityChoises.BRAND,
    )
    quantity = models.FloatField(default=0)
    # readonly
    weight_package_g = models.FloatField(default=0, blank=True)

    def save(self, *args, **kwargs):
        self.weight_package_g = self.quantity * int(self.portion.weight_g)
        super(Package, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}  / {self.weight_package_g} g"

    def __repr__(self):
        return self.__str__()

    class Meta:
        ordering = ("name",)


class Price(TimeStampMixin):
    price_eur = models.FloatField()
    retailer = models.ForeignKey(Retailer, on_delete=models.PROTECT, blank=True)
    package = models.ForeignKey(Package, on_delete=models.PROTECT, null=True)

    # readonly
    price_per_kg = models.FloatField(default=1)

    def save(self, *args, **kwargs):
        self.price_per_kg = round(
            self.price_eur / (self.package.weight_package_g / 1000), 2
        )
        self.created_at = datetime.datetime.now()
        super(Price, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.package} - {self.price_eur} € - {self.retailer}"

    def __repr__(self):
        return self.__str__()


class PhysicalActivityLevel(TimeStampMixin):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    value = models.FloatField()

    def __str__(self):
        return f"{self.name} - {self.value}"

    def __repr__(self):
        return self.__str__()


class MealEvent(TimeStampMixin):
    event = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    norm_portions = models.IntegerField()
    activity_factor = models.ForeignKey(
        PhysicalActivityLevel, on_delete=models.PROTECT, null=True, blank=True
    )
    reserve_factor = models.FloatField(default=1.0)
    is_public = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    created_by = models.ManyToManyField(
        User, related_name="meal_event_created_by", blank=True
    )

    def __str__(self):
        return f"{self.event and self.event.name } - {self.norm_portions} Personen"

    def __repr__(self):
        return self.__str__()


class MealDay(TimeStampMixin):
    meal_event = models.ForeignKey(MealEvent, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    max_day_part_factor = models.FloatField(default=1)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.meal_event} {self.date}"

    def __repr__(self):
        return self.__str__()


class Meal(TimeStampMixin):
    name = models.CharField(default="Hauptessen", max_length=255, null=True, blank=True)
    meal_day = models.ForeignKey(MealDay, on_delete=models.CASCADE, null=True)
    day_part_factor = models.FloatField(default=0.33)
    meal_type = models.CharField(
        max_length=10, choices=MealType.choices, default=MealType.LUNCH_WARM
    )
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return self.__str__()


class MealItem(TimeStampMixin):
    recipe = models.ForeignKey(Recipe, on_delete=models.PROTECT)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    factor = models.FloatField(default=1)

    def __str__(self):
        return f"{self.recipe.name} - {self.meal.name}"

    def __repr__(self):
        return self.__str__()


class PollItem(TimeStampMixin):
    item_1 = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="package_item_1"
    )
    item_2 = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="package_item_2"
    )
    winner = models.ForeignKey(
        Package, on_delete=models.PROTECT, related_name="package_winner", null=True
    )

    def __str__(self):
        return f"{self.winner}"

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
@receiver(post_save, sender=Ingredient)
def post_save_recipe(sender, instance, created, **kwargs):
    if not getattr(instance, "processed", False):
        NutriClass = Nutri()
        physical_viscosity = instance.physical_viscosity
        nutri_items = NutriClass.get_nutri_items()
        nutri_points = 0
        for item in nutri_items:
            value = instance._meta.get_field(item).value_from_object(instance)
            temp_points = NutriClass.get_points(item, physical_viscosity, value)
            setattr(instance, f"nutri_points_{item}", temp_points)
            nutri_points = temp_points + nutri_points

        instance.nutri_points = nutri_points
        instance.nutri_class = NutriClass.get_nutri_class(
            "solid", instance.nutri_points
        )
        instance.processed = True
        instance.save()

        if created:
            Portion.objects.create(ingredient=instance, name=f"{instance.name} in g")
