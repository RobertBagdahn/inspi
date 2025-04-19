from django.apps import AppConfig


class GeneralLoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'general.login'
    verbose_name = 'General - Login'

    def ready(self):
        import general.login.signals