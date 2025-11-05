from django.apps import AppConfig


class BadgesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'badges'

    def ready(self):
        # Import signals to register them
        import badges.signals  # noqa
