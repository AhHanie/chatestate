from django.apps import AppConfig
from django.db.backends.signals import connection_created


class EstateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'estate'

    def ready(self):
        """
        Initialize application services when Django starts.
        This method is called once when Django starts.
        """
        # Import here to avoid circular import issues
        from common.service_provider import ServiceProvider
        from .service import EstateService

        # Check if running in main thread to avoid running twice in development
        import sys
        if 'runserver' not in sys.argv:
            return

        def init_services(sender, connection=None, **kwargs):
            """Initialize services after database connection is established"""
            estate_service = ServiceProvider.get_service(EstateService)
            estate_service.initTypes()

        # Connect to the database connection signal
        connection_created.connect(init_services)
