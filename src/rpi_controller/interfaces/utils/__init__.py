import typing
import logging
from datetime import timedelta

from django.utils import timezone

from rpi_controller.interfaces.exceptions import InterfaceUpdateNotRequiredException


if typing.TYPE_CHECKING:
    from datetime import datetime
    from rpi_controller.models import Device


logger = logging.getLogger(__name__)


def is_status_update_required(
        device: typing.Type["Device"], last_status_update_time: typing.Optional["datetime"], update_min_interval: int
) -> None:
    now = timezone.now()
    if last_status_update_time:
        next_refresh_datetime = last_status_update_time + timedelta(seconds=update_min_interval)
        logger.info(
            "[%s '%s'] Check if status update is required. Last update: %s | Next refresh: %s | Now: %s",
            device.__class__.__name__, device.slug, last_status_update_time, next_refresh_datetime, now
        )
        if now < next_refresh_datetime:
            raise InterfaceUpdateNotRequiredException
