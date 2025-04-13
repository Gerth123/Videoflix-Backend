from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users_app'

    def ready(self):
        """
        Override the ready() method to load the signal handlers for the user model

        The signal handlers are loaded by importing the users_app.signals module.
        """
        import users_app.signals
