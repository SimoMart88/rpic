from django.apps import AppConfig


class Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rpi_controller'

    def _register_sensors(self) -> None:
        from rpi_controller.interfaces.sensors.registry import sensor_registry
        from rpi_controller.interfaces.sensors.gpio import Dht22SensorInterface
        from rpi_controller.interfaces.sensors.mock import MockSensorInterface

        sensor_registry.register(Dht22SensorInterface)
        sensor_registry.register(MockSensorInterface)

    def _register_actuators(self) -> None:
        from rpi_controller.interfaces.actuators.registry import actuator_registry
        from rpi_controller.interfaces.actuators.gpio import RelayActuatorInterface
        from rpi_controller.interfaces.actuators.mock import MockActuatorInterface

        actuator_registry.register(RelayActuatorInterface)
        actuator_registry.register(MockActuatorInterface)


    def _register_controllers(self) -> None:
        from rpi_controller.interfaces.controllers.registry import controller_registry
        from rpi_controller.interfaces.controllers.mixed import SensorTemperatureStepScaleFanControllerInterface
        from rpi_controller.interfaces.controllers.mock import MockControllerInterface

        controller_registry.register(SensorTemperatureStepScaleFanControllerInterface)
        controller_registry.register(MockControllerInterface)


    def ready(self) -> None:
        self._register_sensors()
        self._register_actuators()
        self._register_controllers()
