import pytest
import typing

from rpi_controller.tasks import sensor_read_status


if typing.TYPE_CHECKING:
    from rpi_controller.models import Sensor


@pytest.mark.django_db()
def test_sensor_read_status(dummy_sensor: "Sensor") -> None:
    assert not dummy_sensor.last_status_update_time  # Sanity check
    assert dummy_sensor.last_update_status == dummy_sensor.UpdateStatus.NEW  # Sanity check

    sensor_read_status(dummy_sensor.slug)

    dummy_sensor.refresh_from_db()
    assert dummy_sensor.last_status_update_time
    assert dummy_sensor.last_update_status == dummy_sensor.UpdateStatus.SUCCESS
