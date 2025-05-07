from rpi_controller.interfaces import InterfaceRegistry
from rpi_controller.interfaces.controllers.base import ControllerInterface


class ControllerRegistry(InterfaceRegistry):
    pass


controller_registry = ControllerRegistry(ControllerInterface)
