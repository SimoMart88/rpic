import typing
import pytest
from freezegun import freeze_time
from datetime import timedelta
from django.utils.timezone import now


from rpi_controller.monitoring.backends.base import SystemMonitorEntry
from rpi_controller.monitoring.signals import system_monitor_update_handler


if typing.TYPE_CHECKING:
    import types
    from rpi_controller.models import Device
    from _pytest.fixtures import TopRequest
    from pytest import MonkeyPatch




@pytest.mark.django_db()
@freeze_time("2000-01-01 00:00:00.000000")
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_system_monitor_update_handler(
        device_fixture_name: str, request: "TopRequest", system_monitor_mock: "types.ModuleType",
        monkeypatch: "MonkeyPatch"
) -> None:
    monkeypatch.setattr("rpi_controller.monitoring.signals.monitor", system_monitor_mock.monitor)

    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    result_status = {"dummy_key": "dummy_value"}

    dummy_device.status = result_status
    dummy_device.last_update_status = dummy_device.UpdateStatus.SUCCESS

    assert list(system_monitor_mock.monitor.query_entries(
        key=dummy_device.slug, start_time=now() - timedelta(minutes=1), end_time=now() + timedelta(minutes=1)
    )) == []  # Sanity check

    system_monitor_update_handler(sender=dummy_device.__class__, instance=dummy_device)

    expected_field_result = result_status | {"last_update_status": dummy_device.get_last_update_status_display()}
    assert list(system_monitor_mock.monitor.query_entries(
        key=dummy_device.slug, start_time=now() - timedelta(minutes=1), end_time=now() + timedelta(minutes=1)
    )) == [
        SystemMonitorEntry(key=dummy_device.slug, fields=expected_field_result, time=now())
    ]
