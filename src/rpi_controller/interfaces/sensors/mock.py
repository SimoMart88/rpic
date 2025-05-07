import typing
from django import forms

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.sensors.base import SensorInterface


class MockSensorInterfaceForm(ConfigForm):
    user_input_value = forms.CharField(max_length=15)


class MockSensorInterface(SensorInterface):

    label = "MockSensor"
    config_form = MockSensorInterfaceForm
    template_name = "rpi_controller/interfaces/sensors/mock.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {
            "counter": self.context.status.get("counter", 0) + 1,
            "user_input_key": self.context.config.get('user_input_value', 'not configured')
        }
