from django.contrib.auth.models import AbstractUser
from django.db import models
from pictures.models import PictureField


class CustomUser(AbstractUser):
    scout_display_name = models.CharField(max_length=50, default="", unique=True)
    profile_picture = models.ImageField(blank=True, null=True)
    profile_picture = PictureField(
        upload_to="static/profile_images",
        blank=True,
        null=True,
        width_field=200,
        height_field=200,
    )
    about_me = models.TextField(blank=True, null=True, max_length=500)
    stamm = models.CharField(blank=True, null=True, max_length=50)
    bund = models.CharField(blank=True, null=True, max_length=50)

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
            return "Moderator"
        else:
            return "User"

    def written_blogs(self):
        return self.post_set.all()
