import enum
import logging
import importlib
import typing
from abc import ABC, abstractmethod


logger = logging.getLogger(__name__)


@enum.unique
class RelayContactsState(str, enum.Enum):
    NORMALLY_CLOSED = 'NC'
    NORMALLY_OPEN = 'NO'

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:
        return [(item.value, item.name) for item in cls]

    @classmethod
    def get_active_state_map(cls) -> dict[str, typing.Literal[0, 1]]:
        return {
            cls.NORMALLY_CLOSED: 0,
            cls.NORMALLY_OPEN: 1
        }


class IRelay(ABC):
    def __init__(self, gpio_pin: int, contacts_state: RelayContactsState):
        self._gpio_pin: int = gpio_pin
        self._contacts_state = contacts_state
        self.setup()

    @property
    def active_state(self) -> typing.Literal[0, 1]:
        return RelayContactsState.get_active_state_map()[self._contacts_state]

    @abstractmethod
    def setup(self) -> None:
        ...

    @abstractmethod
    def is_active(self, expected_is_active: typing.Optional[bool] = None) -> typing.Optional[bool]:
        ...

    @abstractmethod
    def activate(self) -> None:
        ...

    @abstractmethod
    def deactivate(self) -> None:
        ...

    @abstractmethod
    def close(self) -> None:
        ...


class RelayRPiGPIO(IRelay):
    def setup(self) -> None:
        from RPi import GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._gpio_pin, GPIO.OUT)
        self._client = GPIO

    def is_active(self, expected_is_active: typing.Optional[bool] = False) -> typing.Optional[bool]:
        device_is_active = self._client.input(self._gpio_pin) == self.active_state
        if expected_is_active is not None and device_is_active != expected_is_active:
            logger.warning("Device status (is_active = %s) differ from expected (is_active = %s)",
                           device_is_active, expected_is_active)
        return device_is_active

    def activate(self) -> None:
        self._client.output(self._gpio_pin, self.active_state)

    def deactivate(self) -> None:
        self._client.output(self._gpio_pin, not self.active_state)

    def close(self) -> None:
        pass


class RelayLGPIO(IRelay):
    def __init__(self, gpio_pin: int, contacts_state: RelayContactsState):
        self._client_handler = None
        super().__init__(gpio_pin, contacts_state)

    def setup(self) -> None:
        import lgpio
        self._client_handler = lgpio.gpiochip_open(0)
        lgpio.gpio_claim_output(self._client_handler, self._gpio_pin)
        self._client = lgpio

    def is_active(self, expected_is_active: typing.Optional[bool] = None) -> typing.Optional[bool]:
        # FIXME: lgpio does not support read_input without resetting the device status
        #  so expected value (if any) is use to set it instead of reading it
        if expected_is_active is not None:
            if expected_is_active:
                self.activate()
            else:
                self.deactivate()
        return expected_is_active

    def activate(self) -> None:
        self._client.gpio_write(self._client_handler, self._gpio_pin, self.active_state)

    def deactivate(self) -> None:
        self._client.gpio_write(self._client_handler, self._gpio_pin, not self.active_state)

    def close(self) -> None:
        self._client.gpio_free(self._client_handler, self._gpio_pin)
        self._client.gpiochip_close(self._client_handler)


def create_hardware_interface(gpio_pin: int, contacts_state: RelayContactsState) -> IRelay:
    if importlib.util.find_spec("RPi"):
        return RelayRPiGPIO(gpio_pin, contacts_state)
    else:
        return RelayLGPIO(gpio_pin, contacts_state)
