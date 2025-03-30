from rpi_controller.interfaces import InterfaceRegistry
from rpi_controller.interfaces.actuators.base import ActuatorInterface


class ActuatorRegistry(InterfaceRegistry):
    pass


actuator_registry = ActuatorRegistry(ActuatorInterface)
