from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import models
from django.utils import timezone

from anmelde_tool.email_services import models as email_services_model

from masterdata import models as basic_models
from masterdata.choices import ScoutOrganisationLevelChoices

from general.login.models import CustomUser
from group.models import InspiGroup


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True



class EventPermissionType(models.TextChoices):
    VIEW = "invite", "Veranstaltungseinladung"
    VIEW_NON_PRIVACY = "view_non_privacy", "Daten (nur nicht Datenschutzrelvante)"
    VIEW_ALL = "view_all", "Alle Daten anzeigen (auch Datenschutzrelvante)"
    EDIT = "edit", "Veranstaltung bearbeiten"


class EventRegistrationType(models.Model):
    """
    Model to define the registration level for an event.
    """

    id = models.AutoField(auto_created=True, primary_key=True)
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=100, blank=True)
    level_choice = models.CharField(
        max_length=10,
        choices=ScoutOrganisationLevelChoices.choices,
        default=ScoutOrganisationLevelChoices.STAMM,
        help_text="Art der Anmeldung für die Veranstaltung",
    )
    allowed_multiple_participants = models.BooleanField(
        default=False,
        help_text="Erlaubt die Anmeldung mehrerer Teilnehmer für diese Anmeldestufe",
    )
    need_scout_group = models.BooleanField(
        default=False,
        help_text="Erfordert eine Pfadfindergruppe für diese Anmeldestufe",
    )
    force_single_scout_group = models.BooleanField(
        default=False,
        help_text="Erzwinge, dass nur eine Pfadfindergruppe für jede Gruppe erstellt werden kann.",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Anmeldestufe"
        verbose_name_plural = "Anmeldestufen"
        ordering = ["name"]


class Event(TimeStampMixin):
    name = models.CharField(max_length=50, unique=True)
    slug = models.CharField(max_length=20, unique=True, blank=True, null=True)
    short_description = models.CharField(max_length=100, blank=True)
    long_description = models.CharField(max_length=10000, blank=True)
    cloud_link = models.CharField(max_length=200, blank=True, null=True)
    event_url = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=20, blank=True, null=True)
    location = models.ForeignKey(
        basic_models.EventLocation, on_delete=models.PROTECT, null=True, blank=True
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
    registration_type = models.ForeignKey(
        EventRegistrationType,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="event_registration_type",
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

    @property
    def is_future(self):
        return self.start_date > timezone.now()

    @property
    def total_registrations(self):
        """
        Returns the total number of registrations for the event.
        """
        return self.registrations.count()

    @property
    def total_participants(self):
        """
        Returns the total number of participants for the event.
        """
        return sum(
            registration.participants.count()
            for registration in self.registrations.all()
        )

    @property
    def status(self):
        """
        Returns the status of the event based on the current date and registration deadline.
        """
        now = timezone.now()
        if not self.is_public:
            return "Nicht öffentlich"
        elif self.registration_start and now < self.registration_start:
            return "Vor der Anmeldephase"
        elif (self.registration_deadline and now <= self.registration_deadline) or (
            not self.registration_deadline and self.start_date and now < self.start_date
        ):
            return "Anmeldephase"
        elif self.start_date and now < self.start_date:
            return "Anmeldephase vorbei"
        elif self.end_date and now <= self.end_date:
            return "Veranstaltung findet statt"
        else:
            return "Veranstaltung ist beendet"

    @property
    def role(self):
        """
        Returns the role of the user in relation to the event.
        """
        if self.created_by == self.created_by:
            return "Ersteller"
        else:
            return "Eingeladene"
        
    @property
    def days_until_event(self):
        """
        Returns the number of days until the event starts.
        If the event has already started or there's no start date, returns 0.
        """
        if not self.start_date:
            return 0
        
        now = timezone.now()
        if self.start_date <= now:
            return 0
        
        delta = self.start_date - now
        return delta.days

    def get_absolute_url(self):
        """
        Returns the absolute URL for the event.
        """
        return f"/events/detail/{self.slug}/"

    class Meta:
        verbose_name = "Veranstaltung"
        verbose_name_plural = "Veranstaltungen"
        ordering = ["start_date"]



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

    @property
    def can_edit_event(self):
        return True if self.permission_type == EventPermissionType.EDIT else False

    @property
    def can_view_privacy_event(self):
        return (
            True
            if self.permission_type == EventPermissionType.VIEW_ALL
            or self.permission_type == EventPermissionType.EDIT
            else False
        )

    @property
    def can_view_event(self):
        return (
            True
            if self.permission_type == EventPermissionType.EDIT
            or self.permission_type == EventPermissionType.VIEW_ALL
            or self.permission_type == EventPermissionType.VIEW_NON_PRIVACY
            else False
        )

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
    allow_multiply = models.BooleanField(default=False)
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
    is_public = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="booking_options_created_by",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.price} ({self.event})"

    class Meta:
        verbose_name = "Buchungsoption"
        verbose_name_plural = "Buchungsoptionen"
        ordering = ["name"]


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
