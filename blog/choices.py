from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusType(models.TextChoices):
    DRAFT = "draft", _("Entwurf")
    REVIEW = "review", _("Review")
    PUBLISHED = "published", _("Veröffentlicht")
    ARCHIVED = "archived", _("Archiviert")


class StatusTypeWithAll(models.TextChoices):
    ALL = "all", _("Alle")
    DRAFT = "draft", _("Entwurf")
    REVIEW = "review", _("Review")
    PUBLISHED = "published", _("Veröffentlicht")
    ARCHIVED = "archived", _("Archiviert")


class StatusTypeUser(models.TextChoices):
    DRAFT = "draft", _("Entwurf")
    REVIEW = "review", _("Review")
