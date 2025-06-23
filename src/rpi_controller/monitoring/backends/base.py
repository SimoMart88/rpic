import typing
from datetime import datetime
from dataclasses import dataclass


@dataclass
class SystemMonitorEntry:
    key: str
    time: datetime
    fields: dict[str, typing.Any]

    def __post_init__(self) -> None:
        """
        Validates that the 'time' field is a timezone-aware datetime object.
        """
        if self.time.tzinfo is None:
            raise ValueError(
                f"Time attribute for SystemMonitorEntry (key='{self.key}') must be a timezone-aware datetime. "
                f"Received: {self.time}"
            )

    def split_by(self, field_name: str = "fields") -> typing.Generator["SystemMonitorEntry", None, None]:
        for entry_key, entry_value in getattr(self, field_name).items():
            yield SystemMonitorEntry(
                key=self.key, time=self.time, fields={entry_key: entry_value}
            )

    def to_dict(self) -> dict[str, typing.Any]:
        return {
            "key": self.key,
            "time": self.time,
            "field": self.fields,
        }


class BaseSystemMonitor:
    def __init__(self, params: dict[str, typing.Any]) -> None:
        self._location = params.get("LOCATION", "")
        self._options = params.get("OPTIONS", {})

    def setup(self) -> None:
        """Run operations required to make a SystemMonitor works properly (create folders, created tables, etc...)
        Execution of this code MUST be idempotent.
        """
        raise NotImplementedError(
            "subclasses of BaseTimeseriesStorageWrapper may require a setup() "
            "method"
        )

    def write_entry(self, key:str, fields: dict[str, typing.Any]) -> None:
        raise NotImplementedError(
            "subclasses of BaseTimeseriesStorageWrapper may require a write() "
            "method"
        )

    def query_entries(self, key:str, start_time:"datetime", end_time:"datetime") -> typing.Generator[SystemMonitorEntry, None, None]:
        raise NotImplementedError(
            "subclasses of BaseTimeseriesStorageWrapper may require a query() "
            "method"
        )

    def close(self, **kwargs: typing.Any) -> None:
        pass
