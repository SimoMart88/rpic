import typing

from django.utils.connection import BaseConnectionHandler, ConnectionProxy
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured


if typing.TYPE_CHECKING:
    from rpi_controller.monitoring.backends.base import BaseSystemMonitor


DEFAULT_MONITOR_ALIAS = "default"


class InvalidSystemMonitorBackendError(ImproperlyConfigured):
    pass


class SystemMonitorHandler(BaseConnectionHandler["BaseSystemMonitor"]):
    settings_name = "SYSTEM_MONITORS"
    exception_class = InvalidSystemMonitorBackendError

    def create_connection(self, alias: str) -> "BaseSystemMonitor":
        params = self.settings[alias].copy()
        backend = params.pop("BACKEND")

        try:
            backend_cls = import_string(backend)
        except ImportError as e:
            raise InvalidSystemMonitorBackendError(
                "Could not find backend '%s': %s" % (backend, e)
            ) from e
        return backend_cls(params)


monitors = SystemMonitorHandler()

monitor = ConnectionProxy(monitors, DEFAULT_MONITOR_ALIAS)
