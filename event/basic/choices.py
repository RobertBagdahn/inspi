from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    MALE = 'M', "Männlich"
    FEMALE = 'F', "Weiblich"
    OTHER = 'O', "Divers"
    NOT_SAY = 'N', "Nicht angegeben"

class EatHabit(models.TextChoices):
    VEG = 'V' , "Vegetarisch"
    VEGAN = 'VEG', "Vegan"
    ALL = 'A', "Alles"