import typing
import logging
from copy import copy
from rpi_controller.monitoring import monitor


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device


logger = logging.getLogger(__name__)


def system_monitor_update_handler(sender: typing.Type["Device"], instance: "Device", **kwargs: typing.Any) -> None:
    entry_fields = copy(instance.status)
    entry_fields["last_update_status"] = instance.get_last_update_status_display()

    try:
        monitor.write_entry(key=instance.slug, fields=entry_fields)
    except Exception as e:
        logger.exception("Failed to write SystemMonitor entry for %s: %s", instance.slug, str(e))
