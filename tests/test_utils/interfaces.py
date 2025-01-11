import typing
from django import forms
from rpi_controller.interfaces.sensors.base import SensorInterface


class DummySensorInterfaceForm(forms.Form):
    dummy_input = forms.CharField(max_length=3)


class DummySensorInterface(SensorInterface):
    label = "idummy"
    config_form = DummySensorInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}


class DummySkipLastDatetimeSensorInterface(SensorInterface):
    label = "idummy-skip-last-datetime"
    config_form = DummySensorInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value", "update_last_status_datetime": False}
