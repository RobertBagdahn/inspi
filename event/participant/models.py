import uuid

from django.contrib.auth import get_user_model
from django.db import models

from event.registration import models as registration_models
from event.basic import models as basic_models
from event.basic import choices as basic_choices

from general.login.models import Person

# Create your models here.
class Participant(models.Model):
    scout_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="Generated")
    last_name = models.CharField(max_length=100, default="Generated")
    address = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=5, blank=True)
    email = models.EmailField(null=True, blank=True)
    birthday = models.DateField(null=True, blank=True)
    registration = models.ForeignKey(
        registration_models.Registration, on_delete=models.CASCADE, null=True, blank=True
    )
    booking_option = models.ForeignKey(
        basic_models.BookingOption, on_delete=models.SET_NULL, blank=True, null=True
    )
    gender = models.CharField(
        max_length=1,
        choices=basic_choices.Gender.choices,
        default=basic_choices.Gender.NOT_SAY,
    )
    generated = models.BooleanField(default=False)
    eat_habits = models.CharField(
        max_length=10,
        choices=basic_choices.EatHabit,
        default=basic_choices.EatHabit.ALL,
    )
    person = models.ForeignKey(
        Person, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"{self.registration}: {self.last_name}, {self.first_name}"
