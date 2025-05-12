import logging

from rpi_controller.config.celery import app as celery_app
from rpi_controller.models import Sensor


logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def sensor_read_status(self: celery_app, sensor_slug: int) -> None:
    logger.info("[Sensor '%s'] Read status Celery task: %s", sensor_slug, self.request.id)

    sensor = Sensor.objects.get(slug=sensor_slug)
    sensor.read_status()
