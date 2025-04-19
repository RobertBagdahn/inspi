from django.db.models.signals import post_save
from django.dispatch import receiver

from anmelde_tool.email_services import services
from anmelde_tool.registration.models import Registration


# @receiver(post_save, sender=Registration, dispatch_uid='post_save_registration')
# def post_save_registration(sender: Registration, instance: Registration, created, raw, **kwargs):
#     if created:
#         services.send_registration_created_mail(instance_id=str(instance.id))
