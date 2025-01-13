import typing
import pigpio
from django import forms
from rpi_controller.interfaces.sensors.utils import dht
from rpi_controller.interfaces.sensors.base import SensorInterface
from rpi_controller.interfaces.sensors.registry import sensor_registry
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException)


class Dht22SensorInterfaceForm(forms.Form):
    gpio_pin = forms.CharField(label="GPIO ping reference", max_length=3)



class Dht22SensorInterface(SensorInterface):

    label = "DHT22"
    config_form = Dht22SensorInterfaceForm
    template_name = "rpi_controller/interfaces/sensors/dht22.html"

    def read_input(self) -> dict[str, typing.Any]:
        """
        Implementation based on this example
        https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
        """
        try:
            gpio_pin_raw: str = self.context.config['gpio_pin']
        except KeyError:
            raise InterfaceUserConfigurationException('gpio_pin not defined in config')

        try:
            gpio_pin: int = int(gpio_pin_raw)
        except ValueError:
            raise InterfaceConfigurationException(f'"{gpio_pin_raw}" is not a valid GPIO pin')

        pi = pigpio.pi()
        if not pi.connected:
            raise InterfaceRuntimeException('Could not connect to pigpio')

        try:
            sensor = dht.Sensor(pi, gpio_pin)
            _, _, status, temperature, humidity = sensor.read()
        except Exception as e:
            raise InterfaceRuntimeException('DHT22 sensor unexpected error') from e

        if status == dht.DHT_GOOD:
            return {'temperature': temperature, 'humidity': humidity}
        else:
            raise InterfaceRuntimeException('DHT22 sensor read failure')


sensor_registry.register(Dht22SensorInterface)
