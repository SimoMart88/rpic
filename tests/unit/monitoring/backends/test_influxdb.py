import typing
import pytest
from unittest.mock import Mock
from freezegun import freeze_time
from datetime import datetime, timedelta

from freezegun.api import FakeDatetime

from rpi_controller.monitoring.backends.base import SystemMonitorEntry
from rpi_controller.monitoring.backends.influxdb import InfluxDBv1SystemMonitor

if typing.TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def monitor_init_params() -> dict[str, typing.Any]:
    return {
        "LOCATION": "influxdb://username:password@hostname:8086/dbname",
        "OPTIONS": {"timeout": 30}
    }


@pytest.fixture
def monitor_storage_mock(monkeypatch: "MonkeyPatch") -> Mock:
    client_mock = Mock()
    monkeypatch.setattr("rpi_controller.monitoring.backends.influxdb.InfluxDBClient", client_mock)
    return client_mock


@pytest.fixture
def influxdb_monitor(monitor_storage_mock: Mock, monitor_init_params: dict[str, typing.Any]) -> InfluxDBv1SystemMonitor:
    return InfluxDBv1SystemMonitor(monitor_init_params)


def test_init(monitor_init_params: dict[str, typing.Any]) -> None:
    influxdb_storage = InfluxDBv1SystemMonitor(monitor_init_params)

    assert influxdb_storage._location == "influxdb://username:password@hostname:8086/dbname"
    assert influxdb_storage._options == {"timeout": 30}
    assert influxdb_storage._hostname == "hostname"
    assert influxdb_storage._port == 8086
    assert influxdb_storage._username == "username"
    assert influxdb_storage._password == "password"
    assert influxdb_storage._db_name == "dbname"


def test_storage(monitor_storage_mock: Mock, influxdb_monitor: InfluxDBv1SystemMonitor) -> None:
    _ = influxdb_monitor._storage

    monitor_storage_mock.assert_called_once_with(
        'hostname', 8086, 'username', 'password', 'dbname', timeout=30
    )


def test_setup(influxdb_monitor: InfluxDBv1SystemMonitor) -> None:
    influxdb_monitor._storage.get_list_database = Mock(return_value=[])

    influxdb_monitor.setup()

    influxdb_monitor._storage.create_database.assert_called_once_with('dbname')


def test_setup_noop(influxdb_monitor: InfluxDBv1SystemMonitor) -> None:
    influxdb_monitor._storage.get_list_database = Mock(return_value=[{"name": "dbname"}])

    influxdb_monitor.setup()

    influxdb_monitor._storage.create_database.assert_not_called()


@freeze_time("2000-01-01 00:00:00")
def test_write_entry(influxdb_monitor: InfluxDBv1SystemMonitor) -> None:
    write_points_mock = Mock()
    influxdb_monitor._storage.write_points = write_points_mock

    influxdb_monitor.write_entry("key", {"field_key": "field_value"})

    write_points_mock.assert_called_once_with(
        [
            {
                "measurement": "key",
                "fields": {"field_key": "field_value"},
                "time": "2000-01-01T00:00:00+00:00"
            }
        ]
    )


@freeze_time("2000-01-01 00:00:00")
def test_query_entries(influxdb_monitor: InfluxDBv1SystemMonitor) -> None:
    query_result_mock = Mock()
    query_result_mock.get_points = Mock(return_value=[
        {"time": "2000-01-01T00:00:00.000000Z", "field_key": "field_value"},
        {"time": "2000-01-01T01:00:00.000000Z", "field_key": "field_value_1"}
    ])
    query_points_mock = Mock(return_value=query_result_mock)
    influxdb_monitor._storage.query = query_points_mock

    start_time = datetime.now() - timedelta(days=1)
    end_time = datetime.now() + timedelta(days=1)
    query_output = list(influxdb_monitor.query_entries("key", start_time, end_time))

    query_points_mock.assert_called_once_with(
        'SELECT * FROM "key" WHERE time >= $start_time AND time <= $end_time',
        bind_params={
            'start_time': '1999-12-31T00:00:00+00:00',
            'end_time': '2000-01-02T00:00:00+00:00'
        }
    )
    assert list(query_output) == [
        SystemMonitorEntry(key='key', time=FakeDatetime(2000, 1, 1, 0, 0), fields={'field_key': 'field_value'}),
        SystemMonitorEntry(key='key', time=FakeDatetime(2000, 1, 1, 1, 0), fields={'field_key': 'field_value_1'})
    ]
