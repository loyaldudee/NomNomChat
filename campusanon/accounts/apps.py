from django.apps import AppConfig
import atexit


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        Register cleanup handler for ThreadPoolExecutor when the application shuts down.
        This ensures proper resource cleanup and prevents thread leaks.
        """
        from .utils import shutdown_email_executor
        atexit.register(shutdown_email_executor)
