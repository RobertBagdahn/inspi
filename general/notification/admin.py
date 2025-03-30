from django.contrib import admin

from .models import NotificationTopic, NotificationMessage

# Register your models here.

admin.site.register(NotificationTopic)
admin.site.register(NotificationMessage)