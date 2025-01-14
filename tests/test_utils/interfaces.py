import typing
from django import forms

from rpi_controller.interfaces.exceptions import InterfaceUpdateNotRequiredException, InterfaceRuntimeException
from rpi_controller.interfaces.sensors.base import SensorInterface


class DummySensorInterfaceForm(forms.Form):
    dummy_input = forms.CharField(max_length=3)


class DummySensorInterface(SensorInterface):
    label = "idummy"
    config_form = DummySensorInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}


class DummyUpdateNotRequiredSensorInterface(SensorInterface):
    label = "idummy-update-not-required"
    config_form = DummySensorInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        raise InterfaceUpdateNotRequiredException


class DummyErrorSensorInterface(SensorInterface):
    label = "idummy-error"
    config_form = DummySensorInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        raise InterfaceRuntimeException("Sensor error")
