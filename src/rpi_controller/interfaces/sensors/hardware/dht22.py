import time
import logging
import importlib
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


class IDHT22(ABC):
    def __init__(self, gpio_pin: int) -> None:
        self._gpio_pin: int = gpio_pin
        self.setup()

    @abstractmethod
    def setup(self) -> None:
        ...

    @abstractmethod
    def read(self, retries: int) -> tuple[float, float]:
        ...


class DHT22RPIAdafruit(IDHT22):

    def setup(self) -> None:  # pragma: no cover
        import Adafruit_DHT
        self._client = Adafruit_DHT

    def read(self, retries: int) -> tuple[float, float]:
        humidity, temperature = self._client.read_retry(self._client.DHT22, self._gpio_pin, retries=retries)
        return temperature, humidity


class DHT22AdafruitCircuitPython(IDHT22):

    def setup(self) -> None:  # pragma: no cover
        import board
        import adafruit_dht
        self._client = adafruit_dht.DHT22(getattr(board, f"D{self._gpio_pin}"))

    def read(self, retries: int, retry_delay: int = 2) -> tuple[float, float]:
        last_exception = None

        try:
            for attempt in range(retries + 1):
                try:
                    temperature = self._client.temperature
                    humidity = self._client.humidity
                    return temperature, humidity
                except RuntimeError as ex:
                    last_exception = ex
                    if attempt < retries:
                        logger.warning(f"DHT22 read failed: {str(ex)}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)

            raise last_exception
        finally:
            self._client.exit()


def create_hardware_interface(gpio_pin: int) -> IDHT22:
    if importlib.util.find_spec("Adafruit_DHT"):
        return DHT22RPIAdafruit(gpio_pin)
    else:
        return DHT22AdafruitCircuitPython(gpio_pin)
