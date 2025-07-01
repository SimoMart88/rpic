import typing
import logging
from django import forms
from django.db import models

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.actuators.base import ActuatorInterface
from rpi_controller.interfaces.exceptions import (InterfaceRuntimeException,
                                                  InterfaceUserInputException)
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config


if typing.TYPE_CHECKING:
    from RPi import GPIO


logger = logging.getLogger(__name__)


class RelayContactsState(models.TextChoices):
    CLOSED = 'NC', 'Normally Closed'
    OPEN = 'NO', 'Normally Open'


class RelayInterfaceForm(ConfigForm):
    gpio_pin = forms.CharField(label="GPIO pin reference", max_length=3)
    contacts_state = forms.ChoiceField(
        choices=RelayContactsState.choices, initial=RelayContactsState.OPEN,
    )



class RelayActuatorInterface(ActuatorInterface):

    label = "Relay"
    config_form = RelayInterfaceForm
    template_name = "rpi_controller/interfaces/actuators/relay.html"

    @property
    def contacts_state_active_output_map(self) -> dict[RelayContactsState, int]:
        from RPi import GPIO
        return {
            RelayContactsState.CLOSED: GPIO.LOW,
            RelayContactsState.OPEN: GPIO.HIGH
        }

    def _get_gpio_client(self) -> "GPIO":
        from RPi import GPIO
        GPIO.setmode(GPIO.BCM)
        return GPIO

    def read_input(self) -> dict[str, typing.Any]:
        gpio_pin = get_gpio_pin_from_config(self.context.config)
        contacts_state = self.context.config.get("contacts_state", RelayContactsState.OPEN)

        try:
            logger.info("[Actuator '%s'] Setting up GPIO interface", self.context.slug)
            GPIO = self._get_gpio_client()
            GPIO.setup(gpio_pin, GPIO.OUT)  # MUST be OUT, changing it to IN will cause relay status reset

            logger.info("[Actuator '%s'] Reading relay status", self.context.slug)
            status = GPIO.input(gpio_pin)
            logger.info("[Actuator '%s'] Raw status: %s", self.context.slug, status)
        except Exception as e:
            logger.info("[Actuator '%s'] Unexpected error: %s", self.context.slug, e)
            raise InterfaceRuntimeException('Relay unexpected error') from e

        return {"active": status == self.contacts_state_active_output_map[contacts_state]}


    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            active = kwargs["active"]
        except KeyError:
            try:
                active = args[0]
            except IndexError:
                raise InterfaceUserInputException("'active' input flag is required")

        gpio_pin = get_gpio_pin_from_config(self.context.config)
        contacts_state = self.context.config.get("contacts_state", RelayContactsState.OPEN)

        try:
            logger.info("[Actuator '%s'] Setting up GPIO interface", self.context.slug)
            GPIO = self._get_gpio_client()
            GPIO.setup(gpio_pin, GPIO.OUT)

            if active:
                logger.info("[Actuator '%s'] Moving relay to ON (HIGH)", self.context.slug)
                GPIO.output(gpio_pin, self.contacts_state_active_output_map[contacts_state])
            else:
                logger.info("[Actuator '%s'] Moving relay to OFF (LOW)", self.context.slug)
                GPIO.output(gpio_pin, not self.contacts_state_active_output_map[contacts_state])
        except Exception as e:
            logger.info("[Actuator '%s'] Unexpected error: %s", self.context.slug, e)
            raise InterfaceRuntimeException('Relay unexpected error') from e

        return {"active": active}
