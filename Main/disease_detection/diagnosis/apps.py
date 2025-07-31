from django.apps import AppConfig
import sys

class DiagnosisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diagnosis'

    def ready(self):
        # Avoid loading the model during management commands
        if 'manage.py' in sys.argv:
            return

        from . import views  # Import views here to avoid circular dependency
        views.load_model()
