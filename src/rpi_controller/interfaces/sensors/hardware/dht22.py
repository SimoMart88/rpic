import logging
import importlib
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class IDHT22(ABC):
    def __init__(self, gpio_pin: int):
        self._gpio_pin: int = gpio_pin

    @abstractmethod
    def read(self, retries: int) -> tuple[float, float]:
        ...


class DHT22RPIAdafruit(IDHT22):

    def read(self, retries: int) -> tuple[float, float]:
        import Adafruit_DHT

        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, self._gpio_pin, retries=retries)
        return temperature, humidity


class DHT22AdafruitCircuitPython(IDHT22):

    def read(self, retries: int) -> tuple[float, float]:
        import time
        import board
        import adafruit_dht

        board_gpio = getattr(board, f"D{self._gpio_pin}")
        sensor = adafruit_dht.DHT22(board_gpio)
        temperature = 0.0
        humidity = 0.0

        retry = 0
        while retry < retries:
            try:
                temperature, humidity = sensor.temperature, sensor.humidity
                sensor.exit()
                break
            except RuntimeError as ex:
                retry += 1
                if retry < retries:
                    logger.warning(f"DHT22 read failed: {ex.args[0]}. Retrying in 2 seconds...")
                    time.sleep(2.0)
                    continue
                else:
                    raise ex

        return temperature, humidity


def create_hardware_interface(gpio_pin: int) -> IDHT22:
    if importlib.util.find_spec("Adafruit_DHT"):
        return DHT22RPIAdafruit(gpio_pin)
    else:
        return DHT22AdafruitCircuitPython(gpio_pin)
