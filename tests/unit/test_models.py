from __future__ import annotations
import pytest
import typing
from unittest.mock import Mock

from rpi_controller.exceptions import SensorException, ActuatorException, ControllerException
from rpi_controller.signals import post_device_control

if typing.TYPE_CHECKING:
    from rpi_controller.models import Device, Sensor, Controller
    from _pytest.fixtures import TopRequest


@pytest.fixture
def mock_post_device_control_signal() -> typing.Generator[Mock, None, None]:
    post_device_control_mock = Mock()
    post_device_control.connect(post_device_control_mock)

    yield post_device_control_mock

    post_device_control.disconnect(post_device_control_mock)


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_str(device_fixture_name: str, request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    assert str(dummy_device) == dummy_device.name


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_save_slugify(device_fixture_name: str, request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    dummy_device.name = "String to Slugify"
    dummy_device.slug = ""
    dummy_device.save()

    assert str(dummy_device.slug) == "string-to-slugify"


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
])
def test_device_read_status(device_fixture_name: str, request: "TopRequest",
                            mock_post_device_control_signal: Mock) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    expected_output = {"dummy_key": "dummy_value"}

    assert not dummy_device.status  # Sanity check
    assert not dummy_device.last_status_update_time  # Sanity check
    assert not dummy_device.last_status_update_log  # Sanity check
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.NEW  # Sanity check

    output = dummy_device.read_status()
    dummy_device.refresh_from_db()

    assert output == expected_output
    assert dummy_device.status == expected_output
    assert dummy_device.last_status_update_time
    assert dummy_device.last_status_update_log  == f"{dummy_device.__class__.__name__} status updated successfully"
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.SUCCESS
    mock_post_device_control_signal.assert_called_once_with(
        signal=post_device_control, sender=dummy_device.__class__, instance=dummy_device
    )


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor_update_not_required", id="sensor"),
])
def test_device_read_status_update_not_required(device_fixture_name: str, request: "TopRequest",
                                                mock_post_device_control_signal: Mock) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    original_status = dummy_device.status

    assert not dummy_device.last_status_update_time  # Sanity check

    output = dummy_device.read_status()
    dummy_device.refresh_from_db()

    assert output == original_status
    assert dummy_device.status == original_status
    assert not dummy_device.last_status_update_time
    assert dummy_device.last_status_update_log == "Previous log"
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.SUCCESS
    mock_post_device_control_signal.assert_called_once_with(
        signal=post_device_control, sender=dummy_device.__class__, instance=dummy_device
    )


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name,exception_class", [
    pytest.param("dummy_sensor_error", SensorException, id="sensor"),
    pytest.param("dummy_actuator_error", ActuatorException, id="actuator"),
])
def test_device_read_status_error(device_fixture_name: str, exception_class: typing.Type[Exception],
                                  request: "TopRequest", mock_post_device_control_signal: Mock) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    original_status = dummy_device.status

    assert not dummy_device.last_status_update_time  # Sanity check
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.NEW  # Sanity check

    expected_error_message = f"(Interface Error): {dummy_device.__class__.__name__} error"

    with pytest.raises(exception_class) as ex:
        output = dummy_device.read_status()
        assert output == original_status
        assert str(ex) == expected_error_message

    dummy_device.refresh_from_db()

    assert dummy_device.status == original_status
    assert dummy_device.last_status_update_time
    assert dummy_device.last_status_update_log == expected_error_message
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.FAILURE
    mock_post_device_control_signal.assert_called_once_with(
        signal=post_device_control, sender=dummy_device.__class__, instance=dummy_device
    )


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_update_status(device_fixture_name: str, request: "TopRequest",
                              mock_post_device_control_signal: Mock) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    assert not dummy_device.status  # Sanity check
    assert not dummy_device.last_status_update_time  # Sanity check
    assert not dummy_device.last_status_update_log  # Sanity check
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.NEW  # Sanity check

    output = dummy_device.update_status("my_args", my_kwargs="my_kwargs")
    dummy_device.refresh_from_db()

    expected_output = {"args": ["my_args"], "kwargs": {"my_kwargs": "my_kwargs"}}
    assert output == expected_output
    assert dummy_device.status == expected_output
    assert dummy_device.last_status_update_time
    assert dummy_device.last_status_update_log  == f"{dummy_device.__class__.__name__} status updated successfully"
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.SUCCESS
    mock_post_device_control_signal.assert_called_once_with(
        signal=post_device_control, sender=dummy_device.__class__, instance=dummy_device
    )


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_actuator_update_not_required", id="actuator"),
    pytest.param("dummy_controller_update_not_required", id="controller"),
])
def test_device_update_status_update_not_required(device_fixture_name: str, request: "TopRequest",
                                                  mock_post_device_control_signal: Mock) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    original_status = dummy_device.status

    assert not dummy_device.last_status_update_time  # Sanity check

    output = dummy_device.update_status("my_args", my_kwargs="my_kwargs")
    dummy_device.refresh_from_db()

    assert output == original_status
    assert dummy_device.status == original_status
    assert not dummy_device.last_status_update_time
    assert dummy_device.last_status_update_log == "Previous log"
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.SUCCESS
    mock_post_device_control_signal.assert_called_once_with(
        signal=post_device_control, sender=dummy_device.__class__, instance=dummy_device
    )


@pytest.mark.django_db()
@pytest.mark.parametrize("device_fixture_name,exception_class", [
    pytest.param("dummy_actuator_error", ActuatorException, id="actuator"),
    pytest.param("dummy_controller_error", ControllerException, id="controller"),
])
def test_device_update_status_error(device_fixture_name: str, exception_class: typing.Type[Exception],
                                    request: "TopRequest", mock_post_device_control_signal: Mock) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    original_status = dummy_device.status

    assert not dummy_device.last_status_update_time  # Sanity check
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.NEW  # Sanity check

    expected_error = f"(Interface Error): {dummy_device.__class__.__name__} error"

    with pytest.raises(exception_class) as ex:
        output = dummy_device.update_status("my_args", my_kwargs="my_kwargs")
        assert output == original_status
        assert str(ex) == expected_error

    dummy_device.refresh_from_db()

    assert dummy_device.status == original_status
    assert dummy_device.last_status_update_time
    assert dummy_device.last_status_update_log == expected_error
    assert dummy_device.last_update_status == dummy_device.UpdateStatus.FAILURE
    mock_post_device_control_signal.assert_called_once_with(
        signal=post_device_control, sender=dummy_device.__class__, instance=dummy_device
    )


@pytest.mark.django_db()
def test_sensor_update_status(dummy_sensor: "Sensor") -> None:
    with pytest.raises(NotImplementedError):
        dummy_sensor.update_status()


@pytest.mark.django_db()
def test_controller_read_status(dummy_controller: "Controller") -> None:
    with pytest.raises(NotImplementedError):
        dummy_controller.read_status()
