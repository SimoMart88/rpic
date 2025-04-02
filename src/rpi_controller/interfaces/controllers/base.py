import typing
from abc import abstractmethod

from rpi_controller.interfaces import Interface


class ControllerInterface(Interface):
    @abstractmethod
    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        ...
