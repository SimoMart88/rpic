from __future__ import annotations
import pytest
import typing
from unittest.mock import Mock

from rpi_controller.interfaces.actuators.gpio import RelayActuatorInterface
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException,
                                                  InterfaceUserInputException)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch
    from _pytest.fixtures import TopRequest


@pytest.fixture()
def mock_gpio(monkeypatch: "MonkeyPatch") -> Mock:
    _mock = Mock(
            return_value=Mock(
                is_active=Mock(),
                activate=Mock(),
                deactivate=Mock(),
                close=Mock(),
            )
        )

    monkeypatch.setattr(
        'rpi_controller.interfaces.actuators.gpio.create_hardware_interface',
        _mock
    )

    return _mock


@pytest.fixture()
def mock_gpio_error(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr(
        'rpi_controller.interfaces.actuators.gpio.create_hardware_interface',
        Mock(
            return_value=Mock(
                is_active=Mock(side_effect=InterfaceRuntimeException("ERROR")),
                activate=Mock(side_effect=InterfaceRuntimeException("ERROR")),
                deactivate=Mock(side_effect=InterfaceRuntimeException("ERROR")),
                close=Mock(),
            )
        )
    )


@pytest.fixture()
def mock_gpio_active(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr(
        'rpi_controller.interfaces.actuators.gpio.create_hardware_interface',
        Mock(
            return_value=Mock(
                is_active=Mock(return_value=True),
                activate=Mock(),
                deactivate=Mock(),
                close=Mock(),
            )
        )
    )


@pytest.fixture()
def mock_gpio_inactive(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr(
        'rpi_controller.interfaces.actuators.gpio.create_hardware_interface',
        Mock(
            return_value=Mock(
                is_active=Mock(return_value=False),
                activate=Mock(),
                deactivate=Mock(),
                close=Mock(),
            )
        )
    )


@pytest.mark.parametrize("mock_gpio,expected_active,", [
    pytest.param("mock_gpio_active", True, id="active"),
    pytest.param("mock_gpio_inactive", False, id="inactive"),
])
@pytest.mark.django_db()
def test_relay_actuator_read_input(mock_gpio: str, expected_active: bool, request: "TopRequest") -> None:
    from test_utils.factories import ActuatorFactory

    request.getfixturevalue(mock_gpio)

    actuator = ActuatorFactory(config={'gpio_pin': 7})
    actuator_interface = RelayActuatorInterface(actuator)

    actuator_output = actuator_interface.read_input()
    assert actuator_output['active'] is expected_active


@pytest.mark.parametrize("active_command,expected_gpio_func_called", [
    pytest.param(True, "activate", id="active"),
    pytest.param(False, "deactivate", id="inactive"),
])
@pytest.mark.django_db()
def test_relay_actuator_control(active_command: bool, expected_gpio_func_called: str, mock_gpio: Mock) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})
    actuator_interface = RelayActuatorInterface(actuator)

    actuator_output = actuator_interface.control(active_command)
    assert actuator_output['active'] is active_command

    getattr(mock_gpio(), expected_gpio_func_called).assert_called()


@pytest.mark.django_db()
def test_relay_actuator_read_input_userconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.read_input()


@pytest.mark.django_db()
def test_relay_actuator_read_input_interface_error(mock_gpio_error: None) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.read_input()


@pytest.mark.django_db()
def test_relay_actuator_control_userconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)


@pytest.mark.django_db()
def test_relay_actuator_control_interfaceconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 'INVALID'})

    with pytest.raises(InterfaceConfigurationException, match='"INVALID" is not a valid GPIO pin'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)


@pytest.mark.django_db()
def test_relay_actuator_control_interfaceuserinput_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceUserInputException, match="'active' input flag is required"):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control()


@pytest.mark.django_db()
def test_relay_actuator_control_interface_error(mock_gpio_error: None) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)
