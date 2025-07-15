import typing
import logging
from django import forms

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.actuators.base import ActuatorInterface
from rpi_controller.interfaces.exceptions import (InterfaceRuntimeException,
                                                  InterfaceUserInputException)
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config
from rpi_controller.interfaces.actuators.hardware.relay import RelayContactsState, create_hardware_interface


if typing.TYPE_CHECKING:
    from rpi_controller.interfaces.actuators.hardware.relay import IRelay


logger = logging.getLogger(__name__)


class RelayInterfaceForm(ConfigForm):
    gpio_pin = forms.CharField(label="GPIO pin reference", max_length=3)
    contacts_state = forms.ChoiceField(
        choices=RelayContactsState.choices(), initial=RelayContactsState.NORMALLY_OPEN,
    )



class RelayActuatorInterface(ActuatorInterface):

    label = "Relay"
    config_form = RelayInterfaceForm
    template_name = "rpi_controller/interfaces/actuators/relay.html"

    def read_input(self) -> dict[str, typing.Any]:
        gpio_pin = get_gpio_pin_from_config(self.context.config)
        contacts_state = self.context.config.get("contacts_state", RelayContactsState.NORMALLY_OPEN)

        logger.info("[Actuator '%s'] Setting up GPIO interface", self.context.slug)
        actuator: "IRelay" = create_hardware_interface(gpio_pin, contacts_state)

        try:
            logger.info("[Actuator '%s'] Reading relay status", self.context.slug)
            status = actuator.is_active()
            logger.info("[Actuator '%s'] Raw status: %s", self.context.slug, status)
            return {"active": bool(status)}
        except Exception as e:
            logger.error("[Actuator '%s'] Unexpected error: %s", self.context.slug, e)
            raise InterfaceRuntimeException('Relay unexpected error') from e
        finally:
            actuator.close()


    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            active = kwargs["active"]
        except KeyError:
            try:
                active = args[0]
            except IndexError:
                raise InterfaceUserInputException("'active' input flag is required")

        gpio_pin = get_gpio_pin_from_config(self.context.config)
        contacts_state = self.context.config.get("contacts_state", RelayContactsState.NORMALLY_OPEN)

        logger.info("[Actuator '%s'] Setting up GPIO interface", self.context.slug)
        actuator: "IRelay" = create_hardware_interface(gpio_pin, contacts_state)

        try:
            if active:
                logger.info("[Actuator '%s'] Moving relay to ACTIVATED", self.context.slug)
                actuator.activate()
            else:
                logger.info("[Actuator '%s'] Moving relay to DEACTIVATED", self.context.slug)
                actuator.deactivate()

            return {"active": active}
        except Exception as e:
            logger.error("[Actuator '%s'] Unexpected error: %s", self.context.slug, e)
            raise InterfaceRuntimeException('Relay unexpected error') from e
        finally:
            actuator.close()
