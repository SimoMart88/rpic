import typing
from django import forms
from rpi_controller.interfaces.actuators.base import ActuatorInterface
from rpi_controller.interfaces.actuators.registry import actuator_registry


class MockActuatorInterfaceForm(forms.Form):
    config_value = forms.CharField(max_length=15)


class MockActuatorInterface(ActuatorInterface):

    label = "MockActuator"
    config_form = MockActuatorInterfaceForm
    template_name = "rpi_controller/interfaces/actuators/mock.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return {
            "flag": kwargs.get("active", args[0]),
            "config_value": self.context.config.get('config_value', 'not configured')
        }


actuator_registry.register(MockActuatorInterface)
