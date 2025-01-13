from __future__ import annotations

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from strategy_field.fields import StrategyField

import typing
import logging

from rpi_controller.interfaces.sensors.registry import sensor_registry


logger = logging.getLogger(__name__)


class Device(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    visible = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    status = models.JSONField(default=dict)
    last_status_updated = models.DateTimeField(null=True, blank=True)
    interface = StrategyField()

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise NotImplementedError

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Sensor(Device):
    interface = StrategyField(registry=sensor_registry)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        logger.info("[Sensor '%s'] Read input with config: %s", self.slug, self.config)
        status = self.interface.read_input()
        logger.info("[Sensor '%s'] Read input result: %s", self.slug, status)

        if status.pop('update_last_status_datetime', True):
            self.last_status_updated = timezone.now()
        self.status = status
        self.save()

        return self.status
