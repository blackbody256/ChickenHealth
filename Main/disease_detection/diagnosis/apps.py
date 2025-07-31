from django.apps import AppConfig
import sys

class DiagnosisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diagnosis'

    def ready(self):
        # A check to prevent the model from loading during management commands
        is_management_command = any('manage.py' in arg for arg in sys.argv)
        if is_management_command:
            return

        from . import views
        views.load_model()
