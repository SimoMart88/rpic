import typing
import board
import adafruit_dht
from django import forms
from rpi_controller.interfaces.sensors import SensorInterface, sensor_registry
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException)


class Dht22SensorInterfaceForm(forms.Form):
    gpio_pin = forms.CharField(label="GPIO ping reference", max_length=3)



class Dht22SensorInterface(SensorInterface):

    config_form = Dht22SensorInterfaceForm
    template_name = "rpi_controller/interfaces/sensors/dht22.html"

    def read_input(self) -> dict[str, typing.Any]:
        """
        Implementation based on this example
        https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
        """
        try:
            gpio_pin = self.context.config['gpio_pin']
        except KeyError:
            raise InterfaceUserConfigurationException('gpio_pin not defined in config')

        try:
            board_pin = getattr(board, gpio_pin)
        except AttributeError:
            try:
                board_pin = getattr(board, f'D{gpio_pin}')
            except AttributeError:
                raise InterfaceConfigurationException(f'"{gpio_pin}" is not a valid GPIO pin')

        try:
            sensor = adafruit_dht.DHT22(board_pin)
            return {'temperature': sensor.temperature, 'humidity': sensor.humidity}
        except Exception as e:
            raise InterfaceRuntimeException('Failed to read DHT22 sensor') from e


sensor_registry.register(Dht22SensorInterface)
