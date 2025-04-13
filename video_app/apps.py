from django.apps import AppConfig


class VideoAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_app'

    def ready(self):
        """
        Override the ready() method to load the signal handlers for the video model

        The signal handlers are loaded by importing the video_app.signals module.
        """
        import video_app.signals
