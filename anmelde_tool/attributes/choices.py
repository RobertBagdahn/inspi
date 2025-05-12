from django.db import models
from django.utils.translation import gettext_lazy as _


class TravelType(models.TextChoices):
    Train = "T", _("Öffis")
    Bus = "B", _("Reisebus")
    Car = "C", _("PKW")
    Other = "O", _("Sonstiges")


class AttributeType(models.TextChoices):
    BooleanAttribute = "BoA", _("Ja/Nein-Feld")
    DateTimeAttribute = "TiA", _("Datum/Uhrzeit-Feld")
    DateAttribute = "DaA", _("Datum-Feld")
    IntegerAttribute = "InA", _("Ganzzahl-Feld")
    FloatAttribute = "FlA", _("Dezimalzahl-Feld")
    StringAttribute = "StA", _("Text-Feld")
    HTMLAttribute = "HtA", _("HTML-Feld")
    RadioAttribute = "RaA", _("Radio-Feld")
    MultiSelectAttribute = "MuA", _("Multi-Select-Feld")
    ZipCodeAttribute = "ZiA", _("PLZ-Feld")
    EmailAttribute = "EmA", _("E-Mail-Feld")
    PhoneAttribute = "PhA", _("Telefonnummer-Feld")
    ScoutGroupAttribute = "ScA", _("Pfadfindergruppe-Feld")
