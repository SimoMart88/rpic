import typing
from rpi_controller.interfaces.sensors import SensorInterface


class DummySensorInterface(SensorInterface):
    label = "idummy"

    def read_input(self, gpio_config: dict[str, typing.Any], device_config: dict[str, typing.Any]) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}
