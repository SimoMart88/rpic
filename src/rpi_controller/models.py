from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from strategy_field.fields import StrategyField

import typing
import logging

from rpi_controller.interfaces.sensors.registry import sensor_registry
from rpi_controller.interfaces.actuators.registry import actuator_registry
from rpi_controller.interfaces.exceptions import InterfaceUpdateNotRequiredException, InterfaceException


logger = logging.getLogger(__name__)


class Device(models.Model):
    class UpdateStatus(models.TextChoices):
        NEW = ("NW", 'NEW')
        SUCCESS = ("SC", 'SUCCESS')
        FAILURE = ("FA", 'FAILURE')

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    visible = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    status = models.JSONField(default=dict, help_text="The current status of the device")
    last_update_status = models.CharField(max_length=2, choices=UpdateStatus.choices, default=UpdateStatus.NEW)
    last_status_update = models.DateTimeField(null=True, blank=True)
    last_status_update_log = models.TextField(null=True, blank=True)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise NotImplementedError

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def _get_status_db_value(self) -> typing.Any:
        """Return value as stored on the DB (with JSON encode/decode)"""
        self.refresh_from_db(fields=["status"])
        return self.status

    def _set_success(self) -> None:
        self.last_status_update = timezone.now()
        self.last_status_update_log = f"{self.__class__.__name__} status updated successfully"
        self.last_update_status = self.UpdateStatus.SUCCESS
        self.save()

    def _set_failure(self, error_message: str) -> None:
        self.last_status_update = timezone.now()
        self.last_status_update_log = error_message
        self.last_update_status = self.UpdateStatus.FAILURE
        self.save()

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Sensor(Device):
    interface = StrategyField(registry=sensor_registry)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            logger.info("[Sensor '%s'] Read input with config: %s", self.slug, self.config)
            self.status = self.interface.read_input()
            logger.info("[Sensor '%s'] Read input result: %s", self.slug, self.status)

            self._set_success()
        except InterfaceUpdateNotRequiredException:
            logger.info("[Sensor '%s'] Status update not required")
        except InterfaceException as e:
            self._set_failure(str(e))

        return self._get_status_db_value()


class Actuator(Device):
    interface = StrategyField(registry=actuator_registry)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            logger.info("[Actuator '%s'] Control actuator with input: '%s' + '%s'", self.slug, args, kwargs)
            self.status = self.interface.control(*args, **kwargs)
            logger.info("[Actuator '%s'] Control result: %s", self.slug, self.status)

            self._set_success()
        except InterfaceException as e:
            self._set_failure(str(e))

        return self._get_status_db_value()
