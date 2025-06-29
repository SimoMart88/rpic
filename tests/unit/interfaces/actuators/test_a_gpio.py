from __future__ import annotations
import pytest
import typing
from unittest import mock

from rpi_controller.interfaces.actuators.gpio import RelayActuatorInterface
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


class MockedRelayActuatorInterface(RelayActuatorInterface):
    def _get_gpio_client(self) -> mock.Mock:
        return mock.Mock()


@pytest.mark.django_db()
def test_relayactuator_read_input(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    actuator_interface = MockedRelayActuatorInterface(actuator)
    actuator_output = actuator_interface.read_input()
    assert actuator_output['active'] is False


@pytest.mark.django_db()
def test_relayactuator_read_input_userconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.read_input()


@pytest.mark.django_db()
def test_relayactuator_read_input_interface_error(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import ActuatorFactory

    class MockedRelayActuatorInterfaceError(MockedRelayActuatorInterface):
        def _get_gpio_client(self) -> mock.Mock:
            return mock.Mock(
                input=mock.Mock(side_effect=InterfaceRuntimeException("ERROR"))
            )

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = MockedRelayActuatorInterfaceError(actuator)
        actuator_interface.read_input()


@pytest.mark.django_db()
def test_relayactuator_control(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    actuator_interface = MockedRelayActuatorInterface(actuator)
    actuator_output = actuator_interface.control(True)
    assert actuator_output['active'] is True


@pytest.mark.django_db()
def test_relayactuator_control_userconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)


@pytest.mark.django_db()
def test_relayactuator_control_interfaceconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 'INVALID'})

    with pytest.raises(InterfaceConfigurationException, match='"INVALID" is not a valid GPIO pin'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)


@pytest.mark.django_db()
def test_relayactuator_control_interfaceuserinput_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceConfigurationException, match="'active' input flag is required"):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control()


@pytest.mark.django_db()
def test_relayactuator_control_interface_error(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import ActuatorFactory

    class MockedRelayActuatorInterfaceError(MockedRelayActuatorInterface):
        def _get_gpio_client(self) -> mock.Mock:
            return mock.Mock(
                output=mock.Mock(side_effect=InterfaceRuntimeException("ERROR"))
            )

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = MockedRelayActuatorInterfaceError(actuator)
        actuator_interface.control(True)
