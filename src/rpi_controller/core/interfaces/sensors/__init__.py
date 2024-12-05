from typing import Any
from abc import abstractmethod
from strategy_field.registry import Registry

from rpi_controller.core.interfaces import Interface


class SensorRegistry(Registry):
    pass


class SensorInterface(Interface):
    @abstractmethod
    def read_input(self, gpio_config: dict[str, Any], device_config: dict[str, Any]) -> dict[str, Any]:
        ...
