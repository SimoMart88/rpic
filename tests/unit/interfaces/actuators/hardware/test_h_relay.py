import pytest
import typing
from unittest.mock import Mock
from rpi_controller.interfaces.actuators.hardware.relay import (
    RelayRPiGPIO, RelayLGPIO, RelayContactsState, create_hardware_interface
)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


class RelayRPiGPIODummy(RelayRPiGPIO):
    def setup(self) -> None:
        self._client = Mock(input=Mock(return_value=True))


class RelayLGPIOPythonDummy(RelayLGPIO):
    def setup(self) -> None:
        self._client = Mock(gpio_write=Mock(return_value=True))


@pytest.mark.parametrize("contact_state,expected_output", [
    pytest.param(RelayContactsState.NORMALLY_OPEN, True, id="NORMALLY_OPEN"),
    pytest.param(RelayContactsState.NORMALLY_CLOSED, False, id="NORMALLY_CLOSED")
])
def test_relayrpigpio_is_active(contact_state: RelayContactsState, expected_output: bool) -> None:
    actuator = RelayRPiGPIODummy(7, contact_state)
    assert actuator.is_active() is expected_output
    actuator._client.input.assert_called_once()


@pytest.mark.parametrize("method_name", [
    pytest.param("activate", id="activate"),
    pytest.param("deactivate", id="deactivate")
])
def test_relayrpigpio_activation(method_name: str) -> None:
    actuator = RelayRPiGPIODummy(7, RelayContactsState.NORMALLY_OPEN)
    getattr(actuator, method_name)()
    actuator._client.output.assert_called_once()


@pytest.mark.parametrize("contact_state,expected_output", [
    pytest.param(RelayContactsState.NORMALLY_OPEN, True, id="NORMALLY_OPEN"),
    pytest.param(RelayContactsState.NORMALLY_CLOSED, False, id="NORMALLY_CLOSED")
])
def test_relaylgpiopythondummy_is_active(contact_state: RelayContactsState, expected_output: bool) -> None:
    actuator = RelayLGPIOPythonDummy(7, contact_state)
    assert actuator.is_active(expected_output) is expected_output
    actuator._client.gpio_write.assert_called_once()


@pytest.mark.parametrize("method_name", [
    pytest.param("activate", id="activate"),
    pytest.param("deactivate", id="deactivate")
])
def test_relaylgpiopythondummy_activation(method_name: str) -> None:
    actuator = RelayLGPIOPythonDummy(7, RelayContactsState.NORMALLY_OPEN)
    getattr(actuator, method_name)()
    actuator._client.gpio_write.assert_called_once()


def test_relaylgpiopythondummy_clode() -> None:
    actuator = RelayLGPIOPythonDummy(7, RelayContactsState.NORMALLY_OPEN)
    actuator.close()
    actuator._client.gpio_free.assert_called_once()
    actuator._client.gpiochip_close.assert_called_once()



def test_create_hardware_interface(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr("rpi_controller.interfaces.actuators.hardware.relay.RelayRPiGPIO.setup",
                        Mock())
    monkeypatch.setattr("rpi_controller.interfaces.actuators.hardware.relay.RelayLGPIO.setup",
                        Mock())

    monkeypatch.setattr("rpi_controller.interfaces.actuators.hardware.relay.importlib.util.find_spec",
                        Mock(return_value=True))
    assert isinstance(create_hardware_interface(7, RelayContactsState.NORMALLY_OPEN), RelayRPiGPIO)

    monkeypatch.setattr("rpi_controller.interfaces.actuators.hardware.relay.importlib.util.find_spec",
                        Mock(return_value=False))
    assert isinstance(create_hardware_interface(7, RelayContactsState.NORMALLY_OPEN), RelayLGPIO)
