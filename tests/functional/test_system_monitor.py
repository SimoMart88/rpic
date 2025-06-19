import typing
import pytest
from freezegun import freeze_time
from datetime import timedelta
from django.utils.timezone import now


from rpi_controller.monitoring.backends.base import SystemMonitorEntry


if typing.TYPE_CHECKING:
    import types
    from rpi_controller.models import Device
    from _pytest.fixtures import TopRequest
    from pytest import MonkeyPatch




@pytest.mark.django_db()
@freeze_time("2000-01-01 00:00:00.000000")
@pytest.mark.parametrize("device_fixture_name,operation", [
    pytest.param("dummy_sensor", "read_status", id="sensor"),
    pytest.param("dummy_actuator", "update_status", id="actuator"),
    pytest.param("dummy_controller", "update_status", id="controller"),
])
def test_system_monitor(
        device_fixture_name: str, operation: str, system_monitor_mock: "types.ModuleType",
        monkeypatch: "MonkeyPatch", request: "TopRequest"
) -> None:
    monkeypatch.setattr("rpi_controller.monitoring.signals.monitor", system_monitor_mock.monitor)

    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    assert list(system_monitor_mock.monitor.query_entries(
        key=dummy_device.slug, start_time=now() - timedelta(minutes=1), end_time=now() + timedelta(minutes=1)
    )) == []  # Sanity check

    getattr(dummy_device, operation)()

    dummy_device.refresh_from_db()
    expected_field_result = dummy_device.status | {"last_update_status": dummy_device.get_last_update_status_display()}
    assert list(system_monitor_mock.monitor.query_entries(
        key=dummy_device.slug, start_time=now() - timedelta(minutes=1), end_time=now() + timedelta(minutes=1)
    )) == [
        SystemMonitorEntry(key=dummy_device.slug, fields=expected_field_result, time=now())
    ]
