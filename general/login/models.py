from django.contrib.auth.models import AbstractUser
from django.db import models
from pictures.models import PictureField
from image_cropping import ImageRatioField
import uuid

from event.basic import choices as event_basic_choices


class Person(models.Model):
    """
    Model to save a natural person with or without login
    """

    id = models.UUIDField(
        auto_created=True, primary_key=True, default=uuid.uuid4, editable=False
    )
    scout_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    address = models.CharField(max_length=200, blank=True, null=True)
    address_supplement = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=5, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=event_basic_choices.Gender.choices,
        default=event_basic_choices.Gender.NOT_SAY,
    )
    birthday = models.DateField(null=True, blank=True)
    eat_habits = models.CharField(
        max_length=10,
        choices=event_basic_choices.EatHabit,
        default=event_basic_choices.EatHabit.ALL,
    )
    about_me = models.TextField(blank=True, null=True, max_length=500)
    stamm = models.CharField(blank=True, null=True, max_length=50)
    bund = models.CharField(blank=True, null=True, max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CustomUser(AbstractUser):
    scout_display_name = models.CharField(max_length=50, default="", unique=True)
    profile_picture = models.ImageField(
        blank=True, upload_to="static/profile/uploaded_images", null=True
    )
    profile_cropping = ImageRatioField("profile_picture", "400x400")
    mobile = models.CharField(blank=True, null=True, max_length=50)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

    # read access
    def is_allowed_to_view_full(self, user):
        return user == self or user.is_staff or user.is_superuser

    def is_allowed_to_edit(self, user):
        return user == self or user.is_staff or user.is_superuser

    def display_rank(self):
        if self.is_superuser:
            return "Admin"
        elif self.is_staff:
            return "Team"
        else:
            return "Normaler User"

    def written_blogs(self):
        return self.post_set.all()

    def written_activities(self):
        return self.activity_set.all()
