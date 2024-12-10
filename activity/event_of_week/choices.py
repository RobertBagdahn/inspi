from django.db import models
from django.utils.translation import gettext_lazy as _


class ColorType(models.TextChoices):
    RED = "#CC6063", _('Rot'),
    BLUE = "#4170A4", _('Blau')
    ORANGE = "#E8B12C", _('Orange')

