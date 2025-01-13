from __future__ import annotations
import pytest
import typing


if typing.TYPE_CHECKING:
    from rpi_controller.models import Sensor


@pytest.mark.django_db()
def test_sensor_str(dummy_sensor: Sensor) -> None:
    assert str(dummy_sensor) == dummy_sensor.name


@pytest.mark.django_db()
def test_sensor_save_slugify() -> None:
    from test_utils.factories import SensorFactory

    dummy_sensor_no_slug = SensorFactory.create(name="String to Slugify", slug=None)
    dummy_sensor_no_slug.save()

    assert str(dummy_sensor_no_slug.slug) == "string-to-slugify"


@pytest.mark.django_db()
def test_sensor_use(dummy_sensor: Sensor) -> None:
    assert not dummy_sensor.status  # Sanity check
    assert not dummy_sensor.last_status_updated  # Sanity check

    output = dummy_sensor.use()

    expected_output = {"dummy_key": "dummy_value"}
    assert output == expected_output
    assert dummy_sensor.status == expected_output
    assert dummy_sensor.last_status_updated


@pytest.mark.django_db()
def test_sensor_use_skip_last_status_datetime_update() -> None:
    from test_utils.factories import SensorFactory
    from strategy_field.utils import fqn
    from test_utils.interfaces import DummySkipLastDatetimeSensorInterface

    dummy_sensor_skip_last = SensorFactory.create(interface=fqn(DummySkipLastDatetimeSensorInterface))

    assert not dummy_sensor_skip_last.last_status_updated  # Sanity check

    dummy_sensor_skip_last.use()

    assert not dummy_sensor_skip_last.last_status_updated
    assert "update_last_status_datetime" not in dummy_sensor_skip_last.status
