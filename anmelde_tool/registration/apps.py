from django.apps import AppConfig


class RegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'anmelde_tool.registration'
    verbose_name = 'Anmelde-Tool - Anmeldungen'

    def ready(self):
        import anmelde_tool.registration.signals
