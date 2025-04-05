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
    SUB_RECIPE = "sub_recipe", "Unter Rezept"


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


class HintLevel(models.TextChoices):
    INFO = "info", "Info"
    WARNING = "warn", "Achtung"
    ERROR = "error", "Fehler"


class MinMaxLevel(models.TextChoices):
    MAX = "max", "Maximal"
    MIN = "min", "Minimal"


class ParameterChoice(models.TextChoices):
    weight_g = "weight_g", "Gewicht (g)"
    energy_kj = "energy_kj", "Energie (kJ)"
    protein_g = "protein_g", "Eiweiß (g)"
    fat_g = "fat_g", "Fett (g)"
    fat_sat_g = "fat_sat_g", "Gesättigte Fettsäuren (g)"
    sugar_g = "sugar_g", "Zucker (g)"
    sodium_mg = "sodium_mg", "Natrium (mg)"
    salt_g = "salt_g", "Salz (g)"
    carbohydrate_g = "carbohydrate_g", "Kohlenhydrate (g)"
    fibre_g = "fibre_g", "Ballaststoffe (g)"
    nutri_points = "nutri_points", "Nutri-Score Punkte"
    nutri_class = "nutri_class", "Nutri-Score Klasse"


class RecipeObjective(models.TextChoices):
    health = "health", "Gesundheit"
    taste = "taste", "Geschmack"
    cost = "cost", "Kosten"
    fullfillment = "fullfillment", "Sättigung"
    # time = "time", "Zeit"
    # sustainability = "sustainability", "Nachhaltigkeit"
    # fun = "fun", "Spaß"
    # creativity = "creativity", "Kreativität"
    # tradition = "tradition", "Tradition"
    # regionality = "regionality", "Regionalität"
    # seasonality = "seasonality", "Saisonalität"
    # variety = "variety", "Vielfalt"
    # convenience = "convenience", "Bequemlichkeit"
    # portion_size = "portion_size", "Portionsgröße"
    # leftovers = "leftovers", "Resteverwertung"
    # storage = "storage", "Lagerung"
    # preparation = "preparation", "Vorbereitung"
    # presentation = "presentation", "Präsentation"
    # temperature = "temperature", "Temperatur"
    # texture = "texture", "Konsistenz"
    # colour = "colour", "Farbe"
    # smell = "smell", "Geruch"
