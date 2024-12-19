import typing
import board
import adafruit_dht
from rpi_controller.interfaces.sensors import SensorInterface, sensor_registry
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException)


"""
Implementation based on this example
https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup
"""


class Dht22SensorInterface(SensorInterface):

    # TODO: implement and configure config_form
    # TODO: implement and configure template_name

    def read_input(self) -> dict[str, typing.Any]:
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
