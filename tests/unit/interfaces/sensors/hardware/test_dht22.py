import pytest
import typing
from unittest.mock import Mock, PropertyMock
from rpi_controller.interfaces.sensors.hardware.dht22 import (
    DHT22RPIAdafruit, DHT22AdafruitCircuitPython, create_hardware_interface
)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


class DHT22RPIAdafruitDummy(DHT22RPIAdafruit):
    def _get_client(self) -> typing.Any:
        return Mock(read_retry=Mock(return_value=(50.2, 22.1)))


class DHT22AdafruitCircuitPythonDummy(DHT22AdafruitCircuitPython):
    def _get_client(self) -> typing.Any:
        client = Mock()
        type(client).temperature = PropertyMock(side_effect=[RuntimeError, 22.1])
        type(client).humidity = PropertyMock(return_value=50.2)
        return client


def test_dht22rpiadafruit_read() -> None:
    sensor = DHT22RPIAdafruitDummy(7)
    assert sensor.read(1) == (22.1, 50.2)


def test_dht22adafruitcircuitpython_read() -> None:
    sensor = DHT22AdafruitCircuitPythonDummy(7)
    assert sensor.read(1) == (22.1, 50.2)


def test_dht22adafruitcircuitpython_read_error() -> None:
    sensor = DHT22AdafruitCircuitPythonDummy(7)
    with pytest.raises(RuntimeError):
        assert sensor.read(0) == (22.1, 50.2)


def test_create_hardware_interface(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr("rpi_controller.interfaces.sensors.hardware.dht22.importlib.util.find_spec",
                        Mock(return_value=True))

    assert isinstance(create_hardware_interface(7), DHT22RPIAdafruit)

    monkeypatch.setattr("rpi_controller.interfaces.sensors.hardware.dht22.importlib.util.find_spec",
                        Mock(return_value=False))

    assert isinstance(create_hardware_interface(7), DHT22AdafruitCircuitPython)
