from django.contrib.auth.models import AbstractUser
from django.db import models
from pictures.models import PictureField
from image_cropping import ImageRatioField


class CustomUser(AbstractUser):
    scout_display_name = models.CharField(max_length=50, default="", unique=True)
    profile_picture = models.ImageField(blank=True, upload_to='static/profile/uploaded_images', null=True)
    profile_cropping = ImageRatioField('profile_picture', '400x400')
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
            return "Team"
        else:
            return "Normaler User"

    def written_blogs(self):
        return self.post_set.all()
    
    def written_activities(self):
        return self.activity_set.all()
