from django.apps import AppConfig

class EduroamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.eduroam'
    verbose_name = 'Eduroam'

    def ready(self):
        import apps.eduroam.signals