from __future__ import annotations
import pytest
import typing
from unittest.mock import Mock
from datetime import timedelta
from django.utils import timezone

from rpi_controller.interfaces.sensors.gpio import Dht22SensorInterface
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException,
                                                  InterfaceUpdateNotRequiredException)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture()
def mock_adafruit_dht(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.create_hardware_interface',
        Mock(
            return_value=Mock(
                read=Mock(return_value=(22.1, 50.2))
            )
        )
    )


@pytest.mark.django_db()
def test_dht22sensor(monkeypatch: MonkeyPatch, mock_adafruit_dht: None) -> None:
    from test_utils.factories import SensorFactory

    sensor = SensorFactory(config={'gpio_pin': 7})

    sensor_interface = Dht22SensorInterface(sensor)
    sensor_input = sensor_interface.read_input()
    assert sensor_input['temperature'] == 22.1
    assert sensor_input['humidity'] == 50.2


@pytest.mark.django_db()
def test_dht22sensor_update_not_required() -> None:
    from test_utils.factories import SensorFactory

    prev_last_status_update_time = timezone.now() - timedelta(seconds=10)

    sensor = SensorFactory(
        config={'gpio_pin': 7, 'refresh_min_interval': 180},
        last_status_update_time=prev_last_status_update_time,
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
def test_dht22sensor_interface_error(monkeypatch: MonkeyPatch) -> None:
    from test_utils.factories import SensorFactory

    monkeypatch.setattr(
        'rpi_controller.interfaces.sensors.gpio.create_hardware_interface',
        Mock(
            return_value=Mock(
                read=Mock(return_value=(None, None))
            )
        )
    )

    sensor = SensorFactory(config={'gpio_pin': 7})

    with pytest.raises(InterfaceRuntimeException, match='DHT22 sensor read failure'):
        sensor_interface = Dht22SensorInterface(sensor)
        sensor_interface.read_input()
