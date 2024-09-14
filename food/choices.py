from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    Male = "M", _("Männlich")
    Female = "F", _("Weiblich")
    Divers = "D", _("Divers")
    Nothing = "N", _("Keine Angabe")


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


class Intolerances(models.TextChoices):
    Gluten = "GLUTEN", _("Gluten")
    Lactose = "LACTOSE", _("Laktose")
    Fructose = "FRUCTOSE", _("Fructose")
    Nuts = "NUTS", _("Nüsse")
    Soy = "SOY", _("Soja")
    Legumes = "LEGUMES", _("Hülsenfrüchte")


class MealEventTemplateOptions(models.TextChoices):
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
