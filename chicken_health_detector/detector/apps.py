from django.apps import AppConfig


class DetectorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'detector'


    def ready(self):
        """
        This method is called once when the Django app is ready.
        It's the ideal place to run startup code like loading a model.
        """
        # We import here to avoid potential AppRegistryNotReady errors.
        from . import ml_utils
        ml_utils.initialize_detector()
