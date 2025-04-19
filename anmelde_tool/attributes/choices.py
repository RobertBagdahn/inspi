from django.db import models
from django.utils.translation import gettext_lazy as _


class TravelType(models.TextChoices):
    Train = 'T', _('Öffis')
    Bus = 'B', _('Reisebus')
    Car = 'C', _('PKW')
    Other = 'O', _('Sonstiges')


class AttributeType(models.TextChoices):
    BooleanAttribute = 'BoA', _('Ja/Nein-Feld')
    DateTimeAttribute = 'TiA', _('Datum/Uhrzeit-Feld')
    IntegerAttribute = 'InA', _('Ganzzahl-Feld')
    FloatAttribute = 'FlA', _('Dezimalzahl-Feld')
    StringAttribute = 'StA', _('Text-Feld')
    TravelAttribute = 'TrA', _('Anreise-Feld')
