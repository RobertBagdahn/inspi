from django.db import models
from django.utils.translation import gettext_lazy as _


class OptionType(models.IntegerChoices):
    LIKE = 1, _('Like'),
    DISLIKE = -1, _('Dislike')


class ExecutionTimeChoices(models.TextChoices):
    LESS_THAN_30 = '1', _('<30 min')
    THIRTY = '2', _('30 min')
    SIXTY = '3', _('60 min')
    NINETY = '4', _('90 min')
    MORE = '5', _('mehr als 90 min')


class DifficultyChoices(models.TextChoices):
    EASY = '1', _('Einfach')
    MEDIUM = '2', _('Mittel')
    HARD = '3', _('Schwer')
    

class CostsRatingChoices(models.TextChoices):
    ZERO = '1', '0 €'
    ZERO_FIFTY = '2', '0,50 €'
    ONE = '3', '1,00 €'
    TWO = '4', '2,00 €'
    MORE = '5', 'mehr als 2,00 €'


class PrepairationTimeChoices(models.TextChoices):
    LESS_THAN_30 = '1', _('keine')
    THIRTY = '2', _('5 min')
    SIXTY = '3', _('30 min')
    NINETY = '4', _('60 min')
    MORE = '5', _('mehr als 60 min')

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
