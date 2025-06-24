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



@pytest.mark.django_db()
def test_relayactuator(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import ActuatorFactory

    class MockedRelayActuatorInterface(RelayActuatorInterface):
        _client_mock = mock.Mock()
        def _get_gpio_client(self) -> mock.Mock:
            return self._client_mock

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    actuator_interface = MockedRelayActuatorInterface(actuator)
    actuator_output = actuator_interface.control(True)
    assert actuator_output['active'] is True
    actuator_interface._client_mock.cleanup.assert_called_once()


@pytest.mark.django_db()
def test_relayactuator_userconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)


@pytest.mark.django_db()
def test_relayactuator_interfaceconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 'INVALID'})

    with pytest.raises(InterfaceConfigurationException, match='"INVALID" is not a valid GPIO pin'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control(True)


@pytest.mark.django_db()
def test_relayactuator_interfaceuserinput_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceConfigurationException, match="'active' input flag is required"):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control()


@pytest.mark.django_db()
def test_relayactuator_interface_error(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import ActuatorFactory

    class MockedRelayActuatorInterface(RelayActuatorInterface):
        _client_mock = mock.Mock(
                output=mock.Mock(side_effect=InterfaceRuntimeException("ERROR"))
            )
        def _get_gpio_client(self) -> mock.Mock:
            return self._client_mock

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = MockedRelayActuatorInterface(actuator)
        actuator_interface.control(True)

        actuator_interface._client_mock.cleanup.assert_called_once()
