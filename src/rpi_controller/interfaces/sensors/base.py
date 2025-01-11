import typing
from abc import abstractmethod

from rpi_controller.interfaces import Interface


class SensorInterface(Interface):
    @abstractmethod
    def read_input(self) -> dict[str, typing.Any]:
        ...
