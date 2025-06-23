import typing
from datetime import timedelta
from django.utils.timezone import now

from freezegun import freeze_time

from rpi_controller import monitoring
from rpi_controller.monitoring.backends.base import SystemMonitorEntry
from test_utils.monitoring import DummySystemMonitor


if typing.TYPE_CHECKING:
    import types


def test_monitors(system_monitor_mock: "types.ModuleType") -> None:
    assert list(map(type, monitoring.monitors.all())) == [DummySystemMonitor]


@freeze_time("2000-01-01 00:00:00")
def test_monitor(system_monitor_mock: "types.ModuleType") -> None:
    test_key = "my_key"
    test_fields = {"my_field": "my_value"}

    monitoring.monitor.setup()
    monitoring.monitor.write_entry(
        key=test_key, fields=test_fields
    )
    assert list(monitoring.monitor.query_entries(
        key=test_key, start_time=now() - timedelta(minutes=1), end_time=now() + timedelta(minutes=1)
    )) == [
        SystemMonitorEntry(key=test_key, fields=test_fields, time=now())
    ]
