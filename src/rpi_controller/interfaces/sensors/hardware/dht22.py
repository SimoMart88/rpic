import time
import logging
import importlib
import typing
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class IDHT22(ABC):
    def __init__(self, gpio_pin: int) -> None:
        self._gpio_pin: int = gpio_pin

    @abstractmethod
    def read(self, retries: int) -> tuple[float, float]:
        ...


class DHT22RPIAdafruit(IDHT22):

    def _get_client(self) -> typing.Any:  # pragma: no cover
        import Adafruit_DHT
        return Adafruit_DHT

    def read(self, retries: int) -> tuple[float, float]:
        sensor_client = self._get_client()
        humidity, temperature = sensor_client.read_retry(sensor_client.DHT22, self._gpio_pin, retries=retries)
        return temperature, humidity


class DHT22AdafruitCircuitPython(IDHT22):

    def _get_client(self) -> typing.Any:  # pragma: no cover
        import board
        import adafruit_dht
        return adafruit_dht.DHT22(getattr(board, f"D{self._gpio_pin}"))

    def read(self, retries: int, retry_delay: int = 2) -> tuple[float, float]:
        sensor_client = self._get_client()
        last_exception = None

        try:
            for attempt in range(retries + 1):
                try:
                    temperature = sensor_client.temperature
                    humidity = sensor_client.humidity
                    return temperature, humidity
                except RuntimeError as ex:
                    last_exception = ex
                    if attempt < retries:
                        logger.warning(f"DHT22 read failed: {str(ex)}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)

            raise last_exception
        finally:
            sensor_client.exit()


def create_hardware_interface(gpio_pin: int) -> IDHT22:
    if importlib.util.find_spec("Adafruit_DHT"):
        return DHT22RPIAdafruit(gpio_pin)
    else:
        return DHT22AdafruitCircuitPython(gpio_pin)
