from django.contrib.auth.models import AbstractUser
from django.db import models
from image_cropping import ImageRatioField
import uuid

from anmelde_tool.event.basic import choices as event_basic_choices
from masterdata.models import ScoutHierarchy, ZipCode
from general.login.choices import AUTH_LEVEL_CHOICES


class CustomUser(AbstractUser):
    scout_display_name = models.CharField(max_length=50, default="", unique=True)
    profile_picture = models.ImageField(
        blank=True, upload_to="static/profile/uploaded_images", null=True
    )
    profile_cropping = ImageRatioField("profile_picture", "400x400")
    auth_level = models.IntegerField(choices=AUTH_LEVEL_CHOICES, default=1)

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
    zip_code = models.ForeignKey(
        ZipCode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="person_zip_code",
    )
    city = models.CharField(max_length=100, blank=True, null=True)
    gender = models.CharField(
        max_length=1,
        choices=event_basic_choices.Gender.choices,
        default=event_basic_choices.Gender.NOT_SAY,
    )
    birthday = models.DateField(null=True, blank=True)
    eat_habits = models.ManyToManyField(
        'food.NutritionalTag',
        blank=True,
        related_name="persons_with_restriction",
        help_text="Food restrictions and preferences"
    )
    about_me = models.TextField(blank=True, null=True, max_length=500)
    scout_group = models.ForeignKey(ScoutHierarchy, on_delete=models.SET_NULL, blank=True, null=True)
    mobile = models.CharField(blank=True, null=True, max_length=50)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, null=True, blank=True, related_name="created_persons"
    )
    managed_by = models.ManyToManyField(
        CustomUser,
        related_name="persons_managed",
        blank=True,
        default=None,
    )
    managed_by_group = models.ManyToManyField(
        'group.InspiGroup',
        related_name="persons_managed_group",
        blank=True,
        help_text="Groups that manage this person",
        default=None,
    )
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="person",
    )
