import typing
import pigpio
import logging
from django.db import transaction
from django import forms

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.sensors.utils import dht
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.exceptions import InterfaceRuntimeException
from rpi_controller.interfaces.utils import is_status_update_required
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config


logger = logging.getLogger(__name__)


class Dht22SensorInterfaceForm(ConfigForm):
    gpio_pin = forms.CharField(label="GPIO ping reference", max_length=3)
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

            logger.info("[Sensor '%s'] Trying connect to the pigpio service", context.slug)
            pi = pigpio.pi()
            if not pi.connected:
                logger.error("[Sensor '%s'] Failed to connect to pigpio service", context.slug)
                raise InterfaceRuntimeException('Could not connect to pigpio')

            logger.info("[Sensor '%s'] Trying read data using pigpio service", context.slug)
            try:
                sensor = dht.Sensor(pi, gpio_pin, model=dht.Sensor.Model.DHT22)  # type: ignore[no-untyped-call]
                sensor_output = sensor.read(self.context.config.get("retry_number", sensor.default_retry_number))  # type: ignore[no-untyped-call]
                logger.info("[Sensor '%s'] pigpio service raw output: %s", context.slug, sensor_output)
                _, _, status, temperature, humidity = sensor_output
            except Exception as e:
                logger.info("[Sensor '%s'] Unexpected error: %s", context.slug, e)
                raise InterfaceRuntimeException('DHT22 sensor unexpected error') from e

            if status == sensor.Status.DHT_GOOD:
                return {'temperature': temperature, 'humidity': humidity}
            else:
                raise InterfaceRuntimeException(f'DHT22 sensor read failure ({sensor.Status(status).name})')
