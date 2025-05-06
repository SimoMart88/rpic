import typing

from django import forms

from rpi_controller.interfaces.exceptions import InterfaceUpdateNotRequiredException, InterfaceRuntimeException
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.actuators.base import ActuatorInterface
from rpi_controller.interfaces.controllers.base import ControllerInterface
from rpi_controller.interfaces.forms import ConfigForm


if typing.TYPE_CHECKING:
    from unittest.mock import Mock


class DummyDeviceInterfaceForm(ConfigForm):
    dummy_input = forms.CharField(max_length=3)


class DummySensorInterface(SensorInterface):
    label = "dummysensor"
    config_form = DummyDeviceInterfaceForm
    template_name = "dummy/test.html"

    def read_input(self) -> dict[str, typing.Any]:
        return {"dummy_key": "dummy_value"}


class UpdatedDummySensorInterface(DummySensorInterface):
    label = "dummysensor-mock"
    read_input_mock: typing.Optional[Mock] = None  # Must be defined by class clients

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


class DummyUpdateNotRequiredActuatorInterface(DummyActuatorInterface):
    label = "dummyactuator-update-not-required"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise InterfaceUpdateNotRequiredException


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


class DummyControllerInterface(ControllerInterface):
    label = "dummycontroller"
    config_form = DummyDeviceInterfaceForm
    template_name = "dummy/test.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return {"args": args, "kwargs": kwargs}


class DummyUpdateNotRequiredControllerInterface(DummyControllerInterface):
    label = "dummycontroller-update-not-required"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise InterfaceUpdateNotRequiredException


class DummyControllerErrorInterface(DummyControllerInterface):
    label = "dummycontroller-error"
    template_name = "dummy/test_button.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise InterfaceRuntimeException("Controller error")


class UpdatedDummyControllerInterface(DummyControllerInterface):
    label = "dummycontroller-mock"
    template_name = "dummy/test_button.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return {"flag": not self.context.status.get("flag", False)}
