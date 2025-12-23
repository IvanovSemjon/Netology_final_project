from django.apps import AppConfig


class BackendConfig(AppConfig):
    """
    Для импорта сигналов.
    
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend'
    label = 'backend'

    def ready(self):
        """
        импортируем сигналы.

        """
        import backend.signals
