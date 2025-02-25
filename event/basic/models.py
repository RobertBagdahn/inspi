import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.shortcuts import render
from django.urls import reverse

User = get_user_model()

user = User.objects.get(username="admin")

class Event(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.CharField(max_length=10000, blank=True)
    start_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    end_date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    registration_deadline = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    registration_start = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    last_possible_update = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    is_public = models.BooleanField(default=False)
    responsible_persons = models.ManyToManyField(User)

    def get_absolute_url(self):
        return reverse('event_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return f"{self.name}"


class BookingOption(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    bookable_from = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    bookable_till = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    max_participants = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class EventRegistration(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    event_date = models.DateField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.event_date}"
