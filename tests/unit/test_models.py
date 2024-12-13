from __future__ import annotations
import pytest
import typing


if typing.TYPE_CHECKING:
    from rpi_controller.models import Sensor


@pytest.mark.django_db()
def test_sensor_str(dummy_sensor: Sensor) -> None:
    assert str(dummy_sensor) == dummy_sensor.name


@pytest.mark.django_db()
def test_sensor_use(dummy_sensor: Sensor) -> None:
    assert dummy_sensor.use() == {"dummy_key": "dummy_value"}
