from django.db import models
from django.utils.translation import gettext_lazy as _


class EmotionType(models.TextChoices):
    IN_LOVE = 'in_love', _('Verliebt')
    HAPPY = 'good', _('Gut')
    DISAPPOINTED = 'disappointed', _('Enttäuscht')
    COMPEX = 'complex', _('zu komplex')

class ExecutionTimeChoices(models.TextChoices):
    LESS_THAN_30 = '0', _('<30 min')
    THIRTY = '1', _('30 min')
    SIXTY = '2', _('60 min')
    NINETY = '3', _('90 min')
    MORE = '4', _('mehr als 90 min')


class DifficultyChoices(models.TextChoices):
    EASY = '0', _('Einfach')
    MEDIUM = '1', _('Mittel')
    HARD = '2', _('Schwer')
    

class CostsRatingChoices(models.TextChoices):
    ZERO = '0', '0 €'
    ZERO_FIFTY = '1', '0,50 €'
    ONE = '2', '1,00 €'
    TWO = '3', '2,00 €'
    MORE = '4', 'mehr als 2,00 €'


class PrepairationTimeChoices(models.TextChoices):
    LESS_THAN_30 = '0', _('keine')
    THIRTY = '1', _('5 min')
    SIXTY = '2', _('30 min')
    NINETY = '3', _('60 min')
    MORE = '4', _('mehr als 60 min')

class StatusChoicesAdmin(models.TextChoices):
    DRAFT = '1', _('Entwurf')
    PUBLISHED = '2', _('Veröffentlicht')
    ARCHIVED = '3', _('Achiviert (Unveröffentlicht)')
    REVIEW = '4', _('Review Angefordert')

class StatusChoices(models.TextChoices):
    DRAFT = '1', _('Entwurf')
    ARCHIVED = '3', _('Achiviert (Unveröffentlicht)')
    REVIEW = '4', _('Review Angefordert')

class StatusSearchChoices(models.TextChoices):
    ALL = '0', _('Alle')
    DRAFT = '1', _('Entwurf')
    PUBLISHED = '2', _('Veröffentlicht')
    ARCHIVED = '3', _('Achiviert (Unveröffentlicht)')
    REVIEW = '4', _('Review Angefordert')


class SortChoices(models.TextChoices):
    RANDOM = '0', _('Zufällig')
    OLDEST = '1', _('Älteste')
    MOST_LIKED = '2', _('Favoriten')
    MOST_COMMENTED = '3', _('Am meisten kommentiert')
    NEWEST = '4', _('Neueste')
