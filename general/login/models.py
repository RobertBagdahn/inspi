from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    scout_display_name = models.CharField(max_length=50, default="")
    profile_picture = models.ImageField(blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.email