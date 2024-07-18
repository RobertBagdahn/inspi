from django.db import models
from django.utils.translation import gettext_lazy as _


class Gender(models.TextChoices):
    Male = "M", _("Männlich")
    Female = "F", _("Weiblich")
    Divers = "D", _("Divers")
    Nothing = "N", _("Keine Angabe")
