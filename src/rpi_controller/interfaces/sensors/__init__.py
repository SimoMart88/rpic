import typing
from abc import abstractmethod

from rpi_controller.interfaces import Interface, InterfaceRegistry


class SensorRegistry(InterfaceRegistry):
    pass


class SensorInterface(Interface):
    @abstractmethod
    def read_input(self, config: dict[str, typing.Any]) -> dict[str, typing.Any]:
        ...


sensor_registry = SensorRegistry(SensorInterface)
