import typing
import logging
import RPi
from django import forms
from rpi_controller.interfaces.actuators.base import ActuatorInterface
from rpi_controller.interfaces.actuators.registry import actuator_registry
from rpi_controller.interfaces.exceptions import (InterfaceRuntimeException,
                                                  InterfaceUserInputException)
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config


class RelayInterfaceForm(forms.Form):
    gpio_pin = forms.CharField(label="GPIO ping reference", max_length=3)


logger = logging.getLogger(__name__)


class RelayActuatorInterface(ActuatorInterface):

    label = "Relay"
    config_form = RelayInterfaceForm
    template_name = "rpi_controller/interfaces/actuators/relay.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            active = kwargs["active"]
        except KeyError:
            try:
                active = args[0]
            except IndexError:
                raise InterfaceUserInputException("'active' input flag is required")

        gpio_pin = get_gpio_pin_from_config(self.context.config)

        try:
            GPIO = RPi.GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(gpio_pin, GPIO.OUT)

            if active:
                GPIO.output(gpio_pin, GPIO.HIGH)
            else:
                GPIO.output(gpio_pin, GPIO.LOW)
        except Exception as e:
            raise InterfaceRuntimeException('Relay unexpected error') from e

        return {"active": active}


actuator_registry.register(RelayActuatorInterface)
