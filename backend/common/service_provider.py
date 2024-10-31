from typing import Dict, Type, TypeVar
from estate.service import EstateService

T = TypeVar('T')


class ServiceProvider:
    _instance = None
    _services: Dict[str, object] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceProvider, cls).__new__(cls)
        return cls._instance

    @classmethod
    def get_service(cls, service_class: Type[T]) -> T:
        """
        Get or create a service instance.

        Args:
            service_class: The class of the service to get or create

        Returns:
            An instance of the requested service
        """
        service_name = service_class.__name__

        if service_name not in cls._services:
            cls._services[service_name] = service_class()

        return cls._services[service_name]

    @classmethod
    def clear_services(cls):
        """Clear all registered services - mainly useful for testing"""
        cls._services.clear()


# Register all available services
AVAILABLE_SERVICES = {
    'estate': EstateService
}
