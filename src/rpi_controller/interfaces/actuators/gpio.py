import typing
import logging
from django import forms
from rpi_controller.interfaces.actuators.base import ActuatorInterface
from rpi_controller.interfaces.actuators.registry import actuator_registry
from rpi_controller.interfaces.exceptions import (InterfaceRuntimeException,
                                                  InterfaceUserInputException)
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config


if typing.TYPE_CHECKING:
    from RPi import GPIO


logger = logging.getLogger(__name__)


class RelayInterfaceForm(forms.Form):
    gpio_pin = forms.CharField(label="GPIO ping reference", max_length=3)


class RelayActuatorInterface(ActuatorInterface):

    label = "Relay"
    config_form = RelayInterfaceForm
    template_name = "rpi_controller/interfaces/actuators/relay.html"

    def _get_gpio_client(self) -> "GPIO":
        from RPi import GPIO
        GPIO.setmode(GPIO.BCM)
        return GPIO

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
            logger.info("[Actuator '%s'] Setting up GPIO interface", self.context.slug)
            GPIO = self._get_gpio_client()
            GPIO.setup(gpio_pin, GPIO.OUT)

            if active:
                logger.info("[Actuator '%s'] Moving relay to ON (HIGH)", self.context.slug)
                GPIO.output(gpio_pin, GPIO.HIGH)
            else:
                logger.info("[Actuator '%s'] Moving relay to OFF (LOW)", self.context.slug)
                GPIO.output(gpio_pin, GPIO.LOW)
        except Exception as e:
            logger.info("[Actuator '%s'] Unexpected error: %s", self.context.slug, e)
            raise InterfaceRuntimeException('Relay unexpected error') from e

        return {"active": active}


actuator_registry.register(RelayActuatorInterface)
