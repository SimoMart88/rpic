from __future__ import annotations
import pytest
import typing
from unittest import mock
from datetime import timedelta
from django.utils import timezone

from rpi_controller.interfaces.sensors.gpio import Dht22SensorInterface
from rpi_controller.interfaces.sensors.utils import dht
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException,
                                                  InterfaceUpdateNotRequiredException)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture()
def mock_pigpio(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.pigpio.pi',
        mock.Mock(return_value=mock.Mock(
            connected=True,
            get_current_tick=mock.Mock(return_value=0),
        ))
    )


@pytest.mark.django_db()
def test_dht22sensor(monkeypatch: MonkeyPatch, mock_pigpio: None) -> None:
    from test_utils.factories import SensorFactory

    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.dht.Sensor.read',
        mock.Mock(return_value=(0, 0, dht.Sensor.Status.DHT_GOOD, 22, 50)),
    )

    sensor = SensorFactory(config={'gpio_pin': 7})

    sensor_interface = Dht22SensorInterface(sensor)
    sensor_input = sensor_interface.read_input()
    assert sensor_input['temperature'] == 22
    assert sensor_input['humidity'] == 50


@pytest.mark.django_db()
def test_dht22sensor_update_not_required() -> None:
    from test_utils.factories import SensorFactory

    prev_last_status_update = timezone.now() - timedelta(seconds=10)

    sensor = SensorFactory(
        config={'gpio_pin': 7, 'refresh_min_interval': 180},
        last_status_update=prev_last_status_update,
        status={"actual_status": "OLD"}
    )

    sensor_interface = Dht22SensorInterface(sensor)
    with pytest.raises(InterfaceUpdateNotRequiredException):
        sensor_interface.read_input()


@pytest.mark.django_db()
def test_dht22sensor_userconfig_error() -> None:
    from test_utils.factories import SensorFactory

    sensor = SensorFactory()

    with pytest.raises(InterfaceUserConfigurationException, match='gpio_pin not defined in config'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()


@pytest.mark.django_db()
def test_dht22sensor_interfaceconfig_error() -> None:
    from test_utils.factories import SensorFactory

    sensor = SensorFactory(config={'gpio_pin': 'INVALID'})

    with pytest.raises(InterfaceConfigurationException, match='"INVALID" is not a valid GPIO pin'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()


@pytest.mark.django_db()
def test_dht22sensor_pigpio_connection_error(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import SensorFactory

    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.pigpio.pi',
        mock.Mock(return_value=mock.Mock(connected=False))
    )

    sensor = SensorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='Could not connect to pigpio'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()


@pytest.mark.django_db()
def test_dht22sensor_interface_error(monkeypatch: MonkeyPatch, mock_pigpio: None) -> None:
    from test_utils.factories import SensorFactory

    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.dht.Sensor.read',
        mock.Mock(return_value=(0, 0, dht.Sensor.Status.DHT_BAD_DATA, 22, 50)),
    )

    sensor = SensorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='DHT22 sensor read failure'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()
