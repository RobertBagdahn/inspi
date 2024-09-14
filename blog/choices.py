from django.db import models
from django.utils.translation import gettext_lazy as _


class StatusType(models.TextChoices):
    DRAFT = "draft", _("Draft")
    REVIEW = "review", _("Under Review")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")


class StatusTypeWithAll(models.TextChoices):
    ALL = "all", _("Alle")
    DRAFT = "draft", _("Draft")
    REVIEW = "review", _("Under Review")
    PUBLISHED = "published", _("Published")
    ARCHIVED = "archived", _("Archived")


class StatusTypeUser(models.TextChoices):
    DRAFT = "draft", _("Draft")
    REVIEW = "review", _("Under Review")
