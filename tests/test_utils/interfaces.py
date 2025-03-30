import typing
from unittest.mock import Mock

from django import forms

from rpi_controller.interfaces.exceptions import InterfaceUpdateNotRequiredException, InterfaceRuntimeException
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.actuators.base import ActuatorInterface


class DummyDeviceInterfaceForm(forms.Form):
    dummy_input = forms.CharField(max_length=3)


class DummySensorInterface(SensorInterface):
    label = "dummysensor"
    config_form = DummyDeviceInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}


class UpdatedDummySensorInterface(DummySensorInterface):
    label = "dummysensor-mock"
    read_input_mock = Mock(
        side_effect=[
            {"dummy_key": "updated_dummy_value"},
            {"dummy_key": "updated_dummy_value_another_time"}
        ]
    )

    def read_input(self) -> dict[str, typing.Any]:
        return self.read_input_mock()


class DummyUpdateNotRequiredSensorInterface(DummySensorInterface):
    label = "dummysensor-update-not-required"

    def read_input(self) -> dict[str, typing.Any]:
        raise InterfaceUpdateNotRequiredException


class DummyErrorSensorInterface(DummySensorInterface):
    label = "dummysensor-error"

    def read_input(self) -> dict[str, typing.Any]:
        raise InterfaceRuntimeException("Sensor error")


class DummyActuatorInterface(ActuatorInterface):
    label = "dummyactuator"
    config_form = DummyDeviceInterfaceForm
    template_name = "dummy/test.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return {"args": args, "kwargs": kwargs}


class DummyActuatorErrorInterface(DummyActuatorInterface):
    label = "dummyactuator-error"
    template_name = "dummy/test_flag.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise InterfaceRuntimeException("Actuator error")


class UpdatedDummyActuatorInterface(DummyActuatorInterface):
    label = "dummyactuator-mock"
    template_name = "dummy/test_flag.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return {"flag": kwargs["flag"]}
