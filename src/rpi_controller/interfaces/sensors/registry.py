from rpi_controller.interfaces import InterfaceRegistry
from rpi_controller.interfaces.sensors.base import SensorInterface


class SensorRegistry(InterfaceRegistry):
    pass


sensor_registry = SensorRegistry(SensorInterface)
