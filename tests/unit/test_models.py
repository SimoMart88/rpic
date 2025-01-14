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
    expected_output = {"dummy_key": "dummy_value"}

    assert not dummy_sensor.status  # Sanity check
    assert not dummy_sensor.last_status_update  # Sanity check
    assert not dummy_sensor.last_status_update_log  # Sanity check
    assert dummy_sensor.last_update_status == dummy_sensor.UpdateStatus.NEW  # Sanity check

    output = dummy_sensor.use()
    dummy_sensor.refresh_from_db()

    assert output == expected_output
    assert dummy_sensor.status == expected_output
    assert dummy_sensor.last_status_update
    assert dummy_sensor.last_status_update_log  == "Sensor status updated successfully"
    assert dummy_sensor.last_update_status == dummy_sensor.UpdateStatus.SUCCESS


@pytest.mark.django_db()
def test_sensor_use_update_not_required() -> None:
    from test_utils.factories import SensorFactory
    from rpi_controller.models import Sensor
    from strategy_field.utils import fqn
    from test_utils.interfaces import DummyUpdateNotRequiredSensorInterface

    expected_output = {"dummy_key": "dummy_value_no_update"}

    dummy_sensor_update_not_required = SensorFactory.create(
        status=expected_output,
        interface=fqn(DummyUpdateNotRequiredSensorInterface),
        last_status_update_log="Previous log",
        last_update_status=Sensor.UpdateStatus.SUCCESS
    )

    assert not dummy_sensor_update_not_required.last_status_update  # Sanity check

    output = dummy_sensor_update_not_required.use()
    dummy_sensor_update_not_required.refresh_from_db()

    assert output == expected_output
    assert dummy_sensor_update_not_required.status == expected_output
    assert not dummy_sensor_update_not_required.last_status_update
    assert dummy_sensor_update_not_required.last_status_update_log == "Previous log"
    assert dummy_sensor_update_not_required.last_update_status == dummy_sensor_update_not_required.UpdateStatus.SUCCESS


@pytest.mark.django_db()
def test_sensor_use_error() -> None:
    from test_utils.factories import SensorFactory
    from strategy_field.utils import fqn
    from test_utils.interfaces import DummyErrorSensorInterface

    expected_output = {"dummy_key": "dummy_value_no_update"}

    dummy_sensor_error = SensorFactory.create(
        status=expected_output,
        interface=fqn(DummyErrorSensorInterface),
    )

    assert not dummy_sensor_error.last_status_update  # Sanity check
    assert dummy_sensor_error.last_update_status == dummy_sensor_error.UpdateStatus.NEW  # Sanity check

    output = dummy_sensor_error.use()
    dummy_sensor_error.refresh_from_db()

    assert output == expected_output
    assert dummy_sensor_error.status == expected_output
    assert not dummy_sensor_error.last_status_update
    assert dummy_sensor_error.last_status_update_log == "Sensor error"
    assert dummy_sensor_error.last_update_status == dummy_sensor_error.UpdateStatus.FAILURE
