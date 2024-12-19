import pytest
import typing
from unittest import mock

from rpi_controller.interfaces.sensors.gpio import Dht22SensorInterface
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture()
def mock_board(monkeypatch: MonkeyPatch) -> str:
    gpio_pin = 'D0'
    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.board',
        mock.Mock(spec=[gpio_pin], gpio_pin=mock.Mock())
    )
    return gpio_pin


@pytest.mark.django_db()
def test_dht22sensor(monkeypatch: MonkeyPatch, mock_board: str) -> None:
    from test_utils.factories import SensorFactory

    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.adafruit_dht.DHT22',
        mock.Mock(return_value=mock.Mock(temperature=22, humidity=50))
    )

    sensor = SensorFactory(config={'gpio_pin': mock_board})

    sensor_interface = Dht22SensorInterface(sensor)
    sensor_input = sensor_interface.read_input()
    assert sensor_input['temperature'] == 22
    assert sensor_input['humidity'] == 50


@pytest.mark.django_db()
def test_dht22sensor_userconfig_error(monkeypatch:MonkeyPatch) -> None:
    from test_utils.factories import SensorFactory

    sensor = SensorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()


@pytest.mark.django_db()
def test_dht22sensor_config_error(monkeypatch: MonkeyPatch, mock_board: str) -> None:
    from test_utils.factories import SensorFactory

    gpio_pin = f'{mock_board}-ERROR'
    sensor = SensorFactory(config={'gpio_pin': gpio_pin})

    with pytest.raises(InterfaceConfigurationException, match=f'"{gpio_pin}" is not a valid GPIO pin'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()


@pytest.mark.django_db()
def test_dht22sensor_interface_error(monkeypatch: MonkeyPatch, mock_board: str) -> None:
    from test_utils.factories import SensorFactory

    sensor = SensorFactory(config={'gpio_pin': mock_board})

    with pytest.raises(InterfaceRuntimeException, match='Failed to read DHT22 sensor'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()
