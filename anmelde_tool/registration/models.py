import uuid

from django.contrib.auth import get_user_model
from django.db import models

from anmelde_tool.event.basic import choices as event_choices
from anmelde_tool.event.basic.models import Event, BookingOption

from general.login.models import CustomUser, Person
from masterdata import models as basic_models


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True
        verbose_name = "Timestamp"
        verbose_name_plural = "Timestamps"
        ordering = ["-created_at"]


# Create your models here.
class Registration(TimeStampMixin):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, editable=False
    )
    scout_organisation = models.ForeignKey(
        basic_models.ScoutHierarchy, null=True, on_delete=models.PROTECT
    )
    responsible_persons = models.ManyToManyField(CustomUser, blank=True)
    is_confirmed = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.event.name}: {self.scout_organisation}"
    
    class Meta:
        verbose_name = "Registration"
        verbose_name_plural = "Registrations"
        ordering = ["-created_at"]

    @property
    def participant_count(self):
        return 5


class RegistrationParticipant(TimeStampMixin):
    scout_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="Generated")
    last_name = models.CharField(max_length=100, default="Generated")
    address = models.CharField(max_length=100, blank=True)
    zip_code = models.ForeignKey(
        basic_models.ZipCode, on_delete=models.PROTECT, null=True, blank=True
    )
    age = models.IntegerField(null=True, blank=True)
    scout_group = models.ForeignKey(
        basic_models.ScoutHierarchy, on_delete=models.PROTECT, null=True, blank=True
    )
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(null=True, blank=True)
    birthday = models.DateTimeField(null=True, blank=True)
    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, null=True, blank=True
    )
    booking_option = models.ForeignKey(
        BookingOption, on_delete=models.SET_NULL, blank=True, null=True
    )
    gender = models.CharField(
        max_length=1,
        choices=event_choices.Gender.choices,
        default=event_choices.Gender.NOT_SAY,
    )
    generated = models.BooleanField(default=False)
    eat_habit = models.ManyToManyField(basic_models.EatHabit, blank=True)
    leader = models.CharField(
        max_length=6,
        choices=event_choices.LeaderTypes.choices,
        default=event_choices.LeaderTypes.KeineFuehrung,
    )
    scout_level = models.CharField(
        max_length=6,
        choices=event_choices.ScoutLevelTypes.choices,
        default=event_choices.ScoutLevelTypes.Unbekannt,
    )
    person = models.ForeignKey(
        Person, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.registration}: {self.last_name}, {self.first_name}"
    
    class Meta:
        verbose_name = "Registration Participant"
        verbose_name_plural = "Registration Participants"
        ordering = ["-created_at"]


class RegistrationRating(TimeStampMixin):
    id = models.AutoField(auto_created=True, primary_key=True)
    text = models.CharField(max_length=50, default="")
    registration = models.ForeignKey(
        Registration, on_delete=models.CASCADE, null=True, blank=True
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    rating = models.IntegerField(default=0)
    

    def __str__(self):
        return f"{self.registration}: {self.text}"
    

    class Meta:
        verbose_name = "Registration Rating"
        verbose_name_plural = "Registration Ratings"
