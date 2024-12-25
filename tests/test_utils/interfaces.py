import typing
from rpi_controller.interfaces.sensors.base import SensorInterface


class DummySensorInterface(SensorInterface):
    label = "idummy"

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}
