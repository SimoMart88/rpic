from __future__ import annotations
import pytest
import typing


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device, Sensor, Actuator
    from _pytest.fixtures import TopRequest


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
])
def test_device_str(device_fixture_name: "Device", request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    assert str(dummy_device) == dummy_device.name


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
])
def test_device_save_slugify(device_fixture_name: "Device", request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    dummy_device.name = "String to Slugify"
    dummy_device.slug = ""
    dummy_device.save()

    assert str(dummy_device.slug) == "string-to-slugify"


@pytest.mark.django_db()
def test_sensor_read_status(dummy_sensor: "Sensor") -> None:
    expected_output = {"dummy_key": "dummy_value"}

    assert not dummy_sensor.status  # Sanity check
    assert not dummy_sensor.last_status_update_time  # Sanity check
    assert not dummy_sensor.last_status_update_log  # Sanity check
    assert dummy_sensor.last_update_status == dummy_sensor.UpdateStatus.NEW  # Sanity check

    output = dummy_sensor.read_status()
    dummy_sensor.refresh_from_db()

    assert output == expected_output
    assert dummy_sensor.status == expected_output
    assert dummy_sensor.last_status_update_time
    assert dummy_sensor.last_status_update_log  == "Sensor status updated successfully"
    assert dummy_sensor.last_update_status == dummy_sensor.UpdateStatus.SUCCESS


@pytest.mark.django_db()
def test_sensor_read_status_update_not_required(dummy_sensor_update_not_required: "Sensor") -> None:
    original_status = dummy_sensor_update_not_required.status

    assert not dummy_sensor_update_not_required.last_status_update_time  # Sanity check

    output = dummy_sensor_update_not_required.read_status()
    dummy_sensor_update_not_required.refresh_from_db()

    assert output == original_status
    assert dummy_sensor_update_not_required.status == original_status
    assert not dummy_sensor_update_not_required.last_status_update_time
    assert dummy_sensor_update_not_required.last_status_update_log == "Previous log"
    assert dummy_sensor_update_not_required.last_update_status == dummy_sensor_update_not_required.UpdateStatus.SUCCESS


@pytest.mark.django_db()
def test_sensor_read_status_error(dummy_sensor_error: "Sensor") -> None:
    original_status = dummy_sensor_error.status

    assert not dummy_sensor_error.last_status_update_time  # Sanity check
    assert dummy_sensor_error.last_update_status == dummy_sensor_error.UpdateStatus.NEW  # Sanity check

    output = dummy_sensor_error.read_status()
    dummy_sensor_error.refresh_from_db()

    assert output == original_status
    assert dummy_sensor_error.status == original_status
    assert dummy_sensor_error.last_status_update_time
    assert dummy_sensor_error.last_status_update_log == "Sensor error"
    assert dummy_sensor_error.last_update_status == dummy_sensor_error.UpdateStatus.FAILURE


@pytest.mark.django_db()
def test_sensor_update_status(dummy_sensor: "Sensor") -> None:
    with pytest.raises(NotImplementedError):
        dummy_sensor.update_status()


@pytest.mark.django_db()
def test_actuator_read_status(dummy_actuator: "Actuator") -> None:
    with pytest.raises(NotImplementedError):
        dummy_actuator.read_status()


@pytest.mark.django_db()
def test_actuator_update_status(dummy_actuator: "Actuator") -> None:
    assert not dummy_actuator.status  # Sanity check
    assert not dummy_actuator.last_status_update_time  # Sanity check
    assert not dummy_actuator.last_status_update_log  # Sanity check
    assert dummy_actuator.last_update_status == dummy_actuator.UpdateStatus.NEW  # Sanity check

    output = dummy_actuator.update_status("my_args", my_kwargs="my_kwargs")
    dummy_actuator.refresh_from_db()

    expected_output = {"args": ["my_args"], "kwargs": {"my_kwargs": "my_kwargs"}}
    assert output == expected_output
    assert dummy_actuator.status == expected_output
    assert dummy_actuator.last_status_update_time
    assert dummy_actuator.last_status_update_log  == "Actuator status updated successfully"
    assert dummy_actuator.last_update_status == dummy_actuator.UpdateStatus.SUCCESS

@pytest.mark.django_db()
def test_actuator_use_error(dummy_actuator_error: "Actuator") -> None:
    original_status = dummy_actuator_error.status

    assert not dummy_actuator_error.last_status_update_time  # Sanity check
    assert dummy_actuator_error.last_update_status == dummy_actuator_error.UpdateStatus.NEW  # Sanity check

    output = dummy_actuator_error.update_status("my_args", my_kwargs="my_kwargs")
    dummy_actuator_error.refresh_from_db()

    assert output == original_status
    assert dummy_actuator_error.status == original_status
    assert dummy_actuator_error.last_status_update_time
    assert dummy_actuator_error.last_status_update_log == "Actuator error"
    assert dummy_actuator_error.last_update_status == dummy_actuator_error.UpdateStatus.FAILURE
