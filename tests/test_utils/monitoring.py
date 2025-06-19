import typing
from django.utils.timezone import now

from rpi_controller.monitoring.backends.base import BaseSystemMonitor, SystemMonitorEntry


if typing.TYPE_CHECKING:
    from datetime import datetime


class DummySystemMonitor(BaseSystemMonitor):
    display_name = "Dummy"

    def __init__(self, params: dict[str, typing.Any]) -> None:
        super().__init__(params)
        self.__storage: dict[str, dict[str, typing.Any]] = {}

    def setup(self) -> None:
        pass

    def write_entry(self, key:str, fields: dict[str, typing.Any]) -> None:
        self.__storage[key] = {"fields": fields, "time": now()}

    def query_entries(self, key:str, start_time:"datetime", end_time:"datetime") -> typing.Generator[SystemMonitorEntry, None, None]:
        for storage_key, storage_value in self.__storage.items():
            if storage_key == key and start_time <= storage_value["time"] <= end_time:
                yield SystemMonitorEntry(
                    key=key, time=storage_value["time"], fields=storage_value["fields"]
                )
