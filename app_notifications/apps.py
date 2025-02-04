from django.apps import AppConfig

class AppNotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_notifications'
    verbose_name = 'Notifications'

    def ready(self):
        import notifications.signals  # noqa 