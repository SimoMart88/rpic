import pytest
import typing
from unittest.mock import Mock, PropertyMock
from rpi_controller.interfaces.sensors.hardware.dht22 import (
    DHT22RPIAdafruit, DHT22AdafruitCircuitPython, create_hardware_interface
)


if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


class DHT22RPIAdafruitDummy(DHT22RPIAdafruit):
    def setup(self) -> None:
        self._client = Mock(read_retry=Mock(return_value=(50.2, 22.1)))


class DHT22AdafruitCircuitPythonDummy(DHT22AdafruitCircuitPython):
    def setup(self) -> None:
        self._client = Mock()
        type(self._client).temperature = PropertyMock(side_effect=[RuntimeError, 22.1])
        type(self._client).humidity = PropertyMock(return_value=50.2)


def test_dht22rpiadafruit_read() -> None:
    sensor = DHT22RPIAdafruitDummy(7)
    assert sensor.read(1) == (22.1, 50.2)
    sensor._client.read_retry.assert_called_once()


def test_dht22adafruitcircuitpython_read() -> None:
    sensor = DHT22AdafruitCircuitPythonDummy(7)
    assert sensor.read(1) == (22.1, 50.2)
    assert type(sensor._client).__dict__["temperature"].call_count == 2
    assert type(sensor._client).__dict__["humidity"].call_count == 1
    sensor._client.exit.assert_called_once()


def test_dht22adafruitcircuitpython_read_error() -> None:
    sensor = DHT22AdafruitCircuitPythonDummy(7)
    with pytest.raises(RuntimeError):
        assert sensor.read(0) == (22.1, 50.2)
    assert type(sensor._client).__dict__["temperature"].call_count == 1
    assert type(sensor._client).__dict__["humidity"].call_count == 0
    sensor._client.exit.assert_called_once()


def test_create_hardware_interface(monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr("rpi_controller.interfaces.sensors.hardware.dht22.DHT22RPIAdafruit.setup",
                        Mock())
    monkeypatch.setattr("rpi_controller.interfaces.sensors.hardware.dht22.DHT22AdafruitCircuitPython.setup",
                        Mock())

    monkeypatch.setattr("rpi_controller.interfaces.sensors.hardware.dht22.importlib.util.find_spec",
                        Mock(return_value=True))
    assert isinstance(create_hardware_interface(7), DHT22RPIAdafruit)

    monkeypatch.setattr("rpi_controller.interfaces.sensors.hardware.dht22.importlib.util.find_spec",
                        Mock(return_value=False))
    assert isinstance(create_hardware_interface(7), DHT22AdafruitCircuitPython)
