import typing
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException)


def get_gpio_pin_from_config(config: dict[typing.Any, typing.Any]) -> int:
    try:
        gpio_pin_raw: str = config['gpio_pin']
    except KeyError:
        raise InterfaceUserConfigurationException('gpio_pin not defined in config')

    try:
        gpio_pin: int = int(gpio_pin_raw)
    except ValueError:
        raise InterfaceConfigurationException(f'"{gpio_pin_raw}" is not a valid GPIO pin')

    return gpio_pin
