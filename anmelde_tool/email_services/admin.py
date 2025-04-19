from django.contrib import admin

from anmelde_tool.email_services.models import EmailAttachment, EmailPicture

admin.site.register(EmailAttachment)
admin.site.register(EmailPicture)
