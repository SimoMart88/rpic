import typing
import Adafruit_DHT
import logging
from django.db import transaction
from django import forms

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.exceptions import InterfaceRuntimeException
from rpi_controller.interfaces.utils import is_status_update_required
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config


logger = logging.getLogger(__name__)


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
                humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, gpio_pin, retries=retries)
            except Exception as e:
                logger.info("[Sensor '%s'] Unexpected error: %s", context.slug, e)
                raise InterfaceRuntimeException('DHT22 sensor unexpected error') from e

            if humidity is not None and temperature is not None:
                return {'temperature': round(temperature, 1), 'humidity': round(humidity, 1)}
            else:
                raise InterfaceRuntimeException('DHT22 sensor read failure, temperature/humidity not available')
