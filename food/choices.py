from django.db import models
from django.utils.translation import gettext_lazy as _


class SuitLevel(models.TextChoices):
    Nothing = "N", _("keine")
    Medium = "M", _("Mittelmäßig viele")
    JustEvening = "J", _("nur Abends")
    Much = "V", _("sehr viele")


class WarmMeal(models.TextChoices):
    Nothing = "N", _("keine")
    JustLunch = "M", _("nur Mittags")
    JustEvening = "J", _("nur Abends")
    Both = "B", _("Mittags und Abends")


class AnimalProducts(models.TextChoices):
    Vegan = "VEGAN", _("Vegan")
    Vegetarian = "VEG", _("Vegetarisch")
    Meat = "M", _("Fleisch")


class IntoleranceChoices(models.TextChoices):
    Gluten = "GLUTEN", _("Gluten")
    Lactose = "LACTOSE", _("Laktose")
    Fructose = "FRUCTOSE", _("Fructose")
    Nuts = "NUTS", _("Nüsse")
    Soy = "SOY", _("Soja")
    Legumes = "LEGUMES", _("Hülsenfrüchte")
    Alcohol = "ALCOHOL", _("Alkohol")
    Histamine = "HISTAMINE", _("Histamin")
    Egg = "EGG", _("Ei")
    Fish = "FISH", _("Fisch")
    Shellfish = "SHELLFISH", _("Meeresfrüchte")
    Pork = "PORK", _("Schwein")
    Beef = "BEEF", _("Rind")
    Chicken = "CHICKEN", _("Huhn")


class MealEventTemplateOptionsChoices(models.TextChoices):
    FIRST_DINNER = "FD", _("Erstes Abendessen")
    LUNCHPACK = "LP", _("Lunchpaket")
    TSCHAI = "TS", _("Tschai")
    HUNGRY = "HU", _("Hungrig")
    NO_COOLING = "NC", _("Keine Kühlung")


class MealTimeOptions(models.TextChoices):
    SINGLE_EVENING = "SE", _("Einfacher Abend")
    SIMPLE_WEEKEND = "SW", _("Einfaches Wochenende")
    LONG_WEEKEND = "LW", _("Langes Wochenende")
    BREAKFAST_TO_BREAKFAST = "BB", _("Morgen zu Morgen")
    LUNCH_TO_LUNCH = "LL", _("Mittag zu Mittag")
    DINNER_TO_DINNER = "EE", _("Abend bis Abend")


class ChildFrendly(models.TextChoices):
    JUST_CHILD = "JC", _("Nur Kinder")
    CHILD_AND_ADULT = "CA", _("Kinder und Erwachsene")
    ADULT = "AD", _("Nur Erwachsene")



class PhysicalViscosityChoices(models.TextChoices):
    SOLID = "solid", "Essen"
    BEVERAGE = "beverage", "Getränk"


class Units(models.TextChoices):
    VOLUME = "ml", "Millilitter"
    MASS = "g", "Gramm"

class BrandQualityChoises(models.TextChoices):
    OWN = "own", "Eigenmarke"
    BRAND = "brand", "Marke"
    PREMIUM = "premium", "Premium"
    
class RetailerTypeChoise(models.TextChoices):
    SUPERMARKET = "supermarket", "Supermarkt"
    DISCOUNTER = "discounter", "Discounter"
    ORGANIC = "organic", "Bioladen"
    MARKET = "market", "Markt"
    ONLINE = "online", "Online"
    OTHER = "other", "Andere"


class PhysicalActivityLevelChoise(models.TextChoices):
    SCHULUNG = "S", "Schulung"
    Hausfahrt = "H", "Hausfahrt"
    Zeltlager = "Z", "Zeltlager"
    Wanderung = "W", "Wanderung"


class RecipeType(models.TextChoices):
    BREAKFAST = "breakfast", "Frühstück"
    WARN_LUNCH = "warm_meal", "Warme Malzeit"
    COLD_LUNCH = "cold_meal", "Kalte Malzeit"
    DESSERT = "dessert", "Nachtisch"
    SIDE_DISH = "side_dish", "Beilage"
    SNACK = "snack", "Snack"
    DRINK = "drink", "Getränk"
    INGREDIENT = "ingredient", "Zutat"


class MealType(models.TextChoices):
    DRINK = "drinks", "Getränk"
    BREAKFAST = "breakfast", "Frühstück"
    WARN_MEAL = "warm_meal", "Warme Malzeit"
    COLD_MEAL = "cold_meal", "Kalte Malzeit"
    SNACK = "snack", "Snack"


class RecipeStatus(models.TextChoices):
    SIMULATOR = "simulator", "Simulator"
    VERIFIED = "verified", "Verified by Inspi"
    USER_CONENT = "user_conent", "Benutzer erstellt"
    USER_CONENT_PUBLIC = "user_public", "Benutzer Öffentlich"


class IngredientStatus(models.TextChoices):
    VERIFIED = "verified", "Verified by Inspi"
    USER_CONENT = "user_conent", "Benutzer erstellt"
    USER_CONENT_PUBLIC = "user_public", "Benutzer Öffentlich"
    DRAFT = "draft", "Entwurf"