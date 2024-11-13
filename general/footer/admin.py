from django.contrib import admin

from .models import Faq, Message, MessageType

admin.site.register(Faq)
admin.site.register(Message)
admin.site.register(MessageType)

