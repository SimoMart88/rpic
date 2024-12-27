import typing
from django import forms
from rpi_controller.interfaces.sensors.base import SensorInterface


class DummySensorInterfaceForm(forms.Form):
    dummy_input = forms.CharField(max_length=3)


class DummySensorInterface(SensorInterface):
    label = "idummy"
    config_form = DummySensorInterfaceForm

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}
