import uuid

from django.contrib.auth import get_user_model
from django.db import models

from event.basic.models import Event
User = get_user_model()

# Create your models here.
class Registration(models.Model):
    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, editable=False
    )
    scout_organisation = models.CharField(max_length=100)
    responsible_persons = models.ManyToManyField(User)
    is_confirmed = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.event.name}: {self.scout_organisation}"