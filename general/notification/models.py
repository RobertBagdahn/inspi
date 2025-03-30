from django.db import models

class NotificationTopic(models.Model):
    """
    Model to save the notification topic
    """
    name = models.CharField(max_length=100, default="")
    description = models.CharField(max_length=300, default="")
    slug = models.SlugField(max_length=100, unique=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = "Notification Topic"
        verbose_name_plural = "Notification Topics"


