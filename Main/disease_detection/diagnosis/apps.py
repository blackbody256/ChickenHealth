from django.apps import AppConfig

class DiagnosisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diagnosis'

    def ready(self):
        from . import views  # Import views here to avoid circular dependency
        views.load_model()
