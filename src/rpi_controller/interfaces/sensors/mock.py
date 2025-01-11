import typing
from django import forms
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.sensors.registry import sensor_registry


class MockSensorInterfaceForm(forms.Form):
    user_input_value = forms.CharField(max_length=15)


class MockSensorInterface(SensorInterface):

    label = "MockSensor"
    config_form = MockSensorInterfaceForm
    template_name = "rpi_controller/interfaces/sensors/mock.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {
            "mock_key": "mock_value",
            "user_input_key": self.context.config.get('user_input_value', 'not configured')
        }


sensor_registry.register(MockSensorInterface)
