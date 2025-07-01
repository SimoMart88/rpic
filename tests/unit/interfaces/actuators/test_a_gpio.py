from __future__ import annotations
import pytest
import typing
from unittest import mock

from rpi_controller.interfaces.actuators.gpio import RelayActuatorInterface, RelayContactsState
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException,
                                                  InterfaceUserInputException)


if typing.TYPE_CHECKING:
    pass


class MockedRelayActuatorInterface(RelayActuatorInterface):
    def __init__(self, *args: typing.Any, gpio_input_value: int = 0, **kwargs: typing.Any):
        super().__init__(*args, **kwargs)
        self._gpio_input_value = gpio_input_value

    def _get_gpio_client(self) -> mock.Mock:
        return mock.Mock(
            LOW=0,
            HIGH=1,
            OUT=1,
            setup=mock.Mock(),
            input=mock.Mock(return_value=self._gpio_input_value),
            output=mock.Mock()
        )

    @property
    def contacts_state_active_output_map(self) -> dict[RelayContactsState, int]:
        return {
            RelayContactsState.CLOSED: 0,  # LOW
            RelayContactsState.OPEN: 1     # HIGH
        }


@pytest.mark.parametrize("contacts_state,gpio_input,expected_active", [
    (RelayContactsState.OPEN, 0, False),    # NO relay, LOW input -> inactive
    (RelayContactsState.OPEN, 1, True),     # NO relay, HIGH input -> active
    (RelayContactsState.CLOSED, 0, True),   # NC relay, LOW input -> active
    (RelayContactsState.CLOSED, 1, False),  # NC relay, HIGH input -> inactive
])
@pytest.mark.django_db()
def test_relayactuator_read_input(contacts_state: RelayContactsState, gpio_input: int, expected_active: bool) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7, 'contacts_state': contacts_state})
    actuator_interface = MockedRelayActuatorInterface(actuator, gpio_input_value=gpio_input)

    actuator_output = actuator_interface.read_input()
    assert actuator_output['active'] is expected_active


@pytest.mark.parametrize("contacts_state,active_command,expected_gpio_output", [
    (RelayContactsState.OPEN, True, 1),   # NO relay, activate -> HIGH
    (RelayContactsState.OPEN, False, 0),  # NO relay, deactivate -> LOW
    (RelayContactsState.CLOSED, True, 0), # NC relay, activate -> LOW
    (RelayContactsState.CLOSED, False, 1), # NC relay, deactivate -> HIGH
])
@pytest.mark.django_db()
def test_relayactuator_control(contacts_state: RelayContactsState, active_command: bool, expected_gpio_output: int) -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory(config={'gpio_pin': 7, 'contacts_state': contacts_state})
    actuator_interface = MockedRelayActuatorInterface(actuator)

    # Mock the _get_gpio_client to return the same mock instance for verification
    gpio_mock = mock.Mock(
        LOW=0,
        HIGH=1,
        OUT=1,
        setup=mock.Mock(),
        output=mock.Mock()
    )
    actuator_interface._get_gpio_client = mock.Mock(return_value=gpio_mock)  # type: ignore[method-assign]

    actuator_output = actuator_interface.control(active_command)
    assert actuator_output['active'] is active_command

    # Verify GPIO.output was called with expected value
    gpio_mock.output.assert_called_with(7, expected_gpio_output)


@pytest.mark.django_db()
def test_relayactuator_read_input_userconfig_error() -> None:
    from test_utils.factories import ActuatorFactory

    actuator = ActuatorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.read_input()


@pytest.mark.django_db()
def test_relayactuator_read_input_interface_error() -> None:
    from test_utils.factories import ActuatorFactory

    class MockedRelayActuatorInterfaceError(MockedRelayActuatorInterface):
        def _get_gpio_client(self) -> mock.Mock:
            return mock.Mock(
                LOW=0,
                HIGH=1,
                OUT=1,
                setup=mock.Mock(),
                input=mock.Mock(side_effect=InterfaceRuntimeException("ERROR")),
                output=mock.Mock()
            )

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = MockedRelayActuatorInterfaceError(actuator)
        actuator_interface.read_input()


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

    with pytest.raises(InterfaceUserInputException, match="'active' input flag is required"):
        actuator_interface = RelayActuatorInterface(actuator)
        actuator_interface.control()


@pytest.mark.django_db()
def test_relayactuator_control_interface_error() -> None:
    from test_utils.factories import ActuatorFactory

    class MockedRelayActuatorInterfaceError(MockedRelayActuatorInterface):
        def _get_gpio_client(self) -> mock.Mock:
            return mock.Mock(
                LOW=0,
                HIGH=1,
                OUT=1,
                setup=mock.Mock(),
                input=mock.Mock(),
                output=mock.Mock(side_effect=InterfaceRuntimeException("ERROR"))
            )

    actuator = ActuatorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Relay unexpected error'):
        actuator_interface = MockedRelayActuatorInterfaceError(actuator)
        actuator_interface.control(True)
