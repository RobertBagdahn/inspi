from django.apps import AppConfig


class ParticipantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event.participant'
    verbose_name = 'Event - Participant'
