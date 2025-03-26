import typing
import pigpio
import logging
from datetime import timedelta
from django.utils import timezone
from django.db import transaction
from django import forms
from rpi_controller.interfaces.sensors.utils import dht
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.sensors.registry import sensor_registry
from rpi_controller.interfaces.exceptions import (InterfaceRuntimeException,
                                                  InterfaceUpdateNotRequiredException)
from rpi_controller.interfaces.utils.gpio import get_gpio_pin_from_config


class Dht22SensorInterfaceForm(forms.Form):
    gpio_pin = forms.CharField(label="GPIO ping reference", max_length=3)
    refresh_min_interval = forms.IntegerField(label="Sensor refresh minimum interval (in seconds)", min_value=5)
    retry_number = forms.IntegerField(label="Sensor retry number", min_value=5)


logger = logging.getLogger(__name__)


class Dht22SensorInterface(SensorInterface):

    label = "DHT22"
    config_form = Dht22SensorInterfaceForm
    template_name = "rpi_controller/interfaces/sensors/dht22.html"

    def read_input(self) -> dict[str, typing.Any]:
        now = timezone.now()
        if self.context.last_status_update_time:
            next_refresh_datetime = self.context.last_status_update_time + timedelta(
                seconds=self.context.config.get("refresh_min_interval", 60)
            )
            logger.info(
                "[Sensor '%s'] Check if status update is required. Last update: %s | Next refresh: %s | Now: %s",
                self.context.slug, self.context.last_status_update_time, next_refresh_datetime, now
            )
            if now < next_refresh_datetime:
                raise InterfaceUpdateNotRequiredException

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


sensor_registry.register(Dht22SensorInterface)
