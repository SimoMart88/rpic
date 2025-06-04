import typing
from urllib.parse import urlparse
from influxdb import InfluxDBClient
from django.utils.functional import cached_property
from datetime import datetime, timezone

from .base import BaseSystemMonitor, SystemMonitorEntry


class InfluxDBv1SystemMonitor(BaseSystemMonitor):
    display_name = "InfluxDBv1"

    def __init__(self, params: dict[str, typing.Any]) -> None:
        super().__init__(params)

        self._class = InfluxDBClient
        self._hostname, self._port, self._username, self._password, self._db_name = self._parse_location()

    def _parse_location(self) -> tuple[str, int, str, str, str]:
        parts = urlparse(self._location)
        return parts.hostname, parts.port, parts.username, parts.password, parts.path.lstrip("/")

    @cached_property
    def _storage(self) -> InfluxDBClient:
        return self._class(self._hostname, self._port, self._username, self._password, self._db_name, **self._options)

    def setup(self) -> None:
        if self._db_name not in [db_info['name'] for db_info in self._storage.get_list_database()]:
            self._storage.create_database(self._db_name)

    def write_entry(self, key:str, fields: dict[str, typing.Any]) -> None:
        json_body = [
            {
                "measurement": key,
                "fields": fields,
                "time": datetime.now(tz=timezone.utc).isoformat()
            }
        ]
        self._storage.write_points(json_body)

    def query_entries(self, key:str, start_time:"datetime", end_time:"datetime") -> typing.Generator[SystemMonitorEntry, None, None]:
        # FIXME: Code prone to SQLInjection,
        #  'key' is passed to the query using string interpolation since bind_params works only for where clause
        #  see https://xginn8-influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdb.InfluxDBClient.query
        query_result = self._storage.query(
            f'SELECT * FROM "{key}" WHERE time >= $start_time AND time <= $end_time',
            bind_params={
                "start_time": start_time.astimezone(tz=timezone.utc).isoformat(),
                "end_time": end_time.astimezone(tz=timezone.utc).isoformat()
            }
        )

        for point in query_result.get_points():
            yield SystemMonitorEntry(
                key=key, time=datetime.strptime(point.pop("time"), "%Y-%m-%dT%H:%M:%S.%fZ"), fields=point
            )
