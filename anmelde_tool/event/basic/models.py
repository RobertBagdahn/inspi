from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models

from anmelde_tool.email_services import models as email_services_model

from masterdata import models as basic_models

from general.login.models import CustomUser
from group.models import InspiGroup


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class EventLocation(TimeStampMixin):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=200, blank=True)
    zip_code = models.ForeignKey(
        basic_models.ZipCode, on_delete=models.PROTECT, null=True, blank=True
    )
    address = models.CharField(max_length=60, blank=True)
    contact_name = models.CharField(max_length=30, blank=True)
    contact_email = models.CharField(max_length=30, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    per_person_fee = models.FloatField(blank=True, null=True)
    fix_fee = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}: ({self.address}, {self.zip_code})"

    class Meta:
        verbose_name = "Event Location"
        verbose_name_plural = "Event Locations"
        ordering = ["name"]


class EventPermissionType(models.TextChoices):
    VIEW = "view", "Veranstaltungseinladung"
    VIEW_NON_PRIVACY = "view_non_privacy", "Daten (nur nicht Datenschutzrelvante)"
    VIEW_ALL = "view_all", "Alle Daten anzeigen (auch Datenschutzrelvante)"
    EDIT = "edit", "Veranstaltung bearbeiten"


class Event(TimeStampMixin):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=20, unique=True, blank=True, null=True)
    short_description = models.CharField(max_length=100, blank=True)
    long_description = models.CharField(max_length=10000, blank=True)
    cloud_link = models.CharField(max_length=200, blank=True, null=True)
    event_url = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=20, blank=True, null=True)
    location = models.ForeignKey(
        EventLocation, on_delete=models.PROTECT, null=True, blank=True
    )
    start_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    end_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    registration_deadline = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    registration_start = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    last_possible_update = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="events_created_by",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name}"

class EventPermission(TimeStampMixin):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_permissions",
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_permissions",
    )
    group = models.ForeignKey(
        InspiGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="event_permissions",
    )
    permission_type = models.CharField(
        max_length=20,
        choices=EventPermissionType.choices,
        default=EventPermissionType.VIEW,
    )
    include_subgroups = models.BooleanField(
        default=True,
        help_text="Falls aktiviert, erhalten auch alle Untergruppen diese Berechtigung",
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="event_permissions_updated_by",
        null=True,
        blank=True,
    )
        
    @property
    def is_group(self):
        return True if self.group else False

        
    def group_user_link(self):
        if self.group:
            return self.group.get_absolute_url()
        elif self.user:
            return self.user.get_absolute_url()
        else:
            return None

    class Meta:
        verbose_name = "Event Permission"
        verbose_name_plural = "Event Permissions"
        constraints = [
            models.CheckConstraint(
                check=(models.Q(user__isnull=False) | models.Q(group__isnull=False)),
                name="event_permission_user_or_group_required",
            )
        ]

    def __str__(self):
        target = self.user.username if self.user else self.group.name
        event = self.event.name if self.event else "No Event"
        return f"{target} - {self.get_permission_type_display()} ({event})"


class EventModule(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=100, default="", blank=True)
    header = models.CharField(max_length=100, default="Default Header")
    description = models.TextField(default="")
    internal = models.BooleanField(default=False)
    ordering = models.IntegerField(default=999, auto_created=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    required = models.BooleanField(default=False)
    standard = models.BooleanField(default=False)
    is_custom = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="event_modules_created_by",
        null=True,
        blank=True,
    )

    def __str__(self):
        if self.event:
            return f"{self.header}"
        else:
            return f"{self.header} (Orginal)"


class BookingOption(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    bookable_from = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    bookable_till = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    max_participants = models.IntegerField(default=0)
    start_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )
    end_date = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True
    )

    def __str__(self):
        return self.name


class StandardEventTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    introduction = models.ForeignKey(
        EventModule, null=True, on_delete=models.PROTECT, related_name="introduction"
    )
    summary = models.ForeignKey(
        EventModule, null=True, on_delete=models.PROTECT, related_name="confirmation"
    )
    participants = models.ForeignKey(
        EventModule, null=True, on_delete=models.PROTECT, related_name="participants"
    )
    letter = models.ForeignKey(
        EventModule, null=True, on_delete=models.PROTECT, related_name="letter"
    )
    other_required_modules = models.ManyToManyField(
        EventModule, blank=True, related_name="other_required_modules"
    )
