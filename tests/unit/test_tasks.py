import pytest
import typing

from rpi_controller.tasks import sensor_read_status, actuator_update_status


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device
    from _pytest.fixtures import TopRequest


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name,task_to_run", [
    pytest.param("dummy_sensor", sensor_read_status, id="sensor"),
    pytest.param("dummy_actuator", actuator_update_status, id="actuator"),
])
def test_task(device_fixture_name: str, task_to_run: typing.Callable[[str], None], request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    assert not dummy_device.last_status_update_time  # Sanity check
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.NEW  # Sanity check

    task_to_run(dummy_device.slug)

    dummy_device.refresh_from_db()
    assert dummy_device.last_status_update_time
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.SUCCESS
