import typing
import logging
from django.db import transaction
from django import forms

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.exceptions import InterfaceRuntimeException
from rpi_controller.interfaces.utils import is_status_update_required
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config
from rpi_controller.interfaces.sensors.hardware.dht22 import create_hardware_interface


logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from rpi_controller.interfaces.sensors.hardware.dht22 import IDHT22


class Dht22SensorInterfaceForm(ConfigForm):
    gpio_pin = forms.CharField(label="GPIO pin reference", max_length=3)
    refresh_min_interval = forms.IntegerField(label="Sensor refresh minimum interval (in seconds)", min_value=5)
    retry_number = forms.IntegerField(label="Sensor retry number", min_value=5)


class Dht22SensorInterface(SensorInterface):

    label = "DHT22"
    config_form = Dht22SensorInterfaceForm
    template_name = "rpi_controller/interfaces/sensors/dht22.html"

    def read_input(self) -> dict[str, typing.Any]:
        is_status_update_required(
            self.context, self.context.last_status_update_time, self.context.config.get("refresh_min_interval", 60)
        )

        with transaction.atomic():
            # Lock model object to avoid concurrent read on the same sensor
            context = type(self.context).objects.select_for_update().get(id=self.context.id)

            gpio_pin = get_gpio_pin_from_config(context.config)
            retries = context.config.get("retry_number", 5)

            try:
                sensor: "IDHT22" = create_hardware_interface(gpio_pin)
                temperature, humidity = sensor.read(retries=retries)
            except Exception as e:
                logger.error("[Sensor '%s'] Unexpected error: %s", context.slug, e)
                raise InterfaceRuntimeException('DHT22 sensor unexpected error') from e

            if humidity is not None and temperature is not None:
                return {'temperature': round(temperature, 1), 'humidity': round(humidity, 1)}
            else:
                raise InterfaceRuntimeException('DHT22 sensor read failure, temperature/humidity not available')
