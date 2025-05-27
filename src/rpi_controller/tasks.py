import typing
import logging

from rpi_controller.config.celery import app as celery_app
from rpi_controller.models import Sensor, Actuator, Controller


logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def sensor_read_status(self: celery_app, sensor_slug: str) -> None:
    logger.info("[Sensor '%s'] Read status Celery task: %s", sensor_slug, self.request.id)

    sensor = Sensor.objects.get(slug=sensor_slug)
    sensor.read_status()


@celery_app.task(bind=True)
def actuator_update_status(self: celery_app, actuator_slug: str, *args: typing.Any, **kwargs: typing.Any) -> None:
    logger.info("[Actuator '%s'] Update status Celery task: %s", actuator_slug, self.request.id)

    actuator = Actuator.objects.get(slug=actuator_slug)
    actuator.update_status(*args, **kwargs)


@celery_app.task(bind=True)
def controller_update_status(self: celery_app, controller_slug: str, *args: typing.Any, **kwargs: typing.Any) -> None:
    logger.info("[Controller '%s'] Update status Celery task: %s", controller_slug, self.request.id)

    controller = Controller.objects.get(slug=controller_slug)
    controller.update_status(*args, **kwargs)
