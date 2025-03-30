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

class NotificationMessage(models.Model):
    """
    Model to save the notification message
    """
    topic = models.ForeignKey(NotificationTopic, on_delete=models.CASCADE, related_name="messages")
    message = models.TextField()
    url = models.URLField(max_length=200, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    send_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic.slug} - {self.message[:20]}..."

    class Meta:
        verbose_name = "Notification Message"
        verbose_name_plural = "Notification Messages"
