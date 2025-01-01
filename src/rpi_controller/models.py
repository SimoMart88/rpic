from __future__ import annotations

from django.db import models
from strategy_field.fields import StrategyField

import typing

from rpi_controller.interfaces.sensors.registry import sensor_registry


class Device(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    visible = models.BooleanField(default=False)
    config = models.JSONField(default=dict)
    interface = StrategyField()

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Sensor(Device):
    interface = StrategyField(registry=sensor_registry)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return self.interface.read_input()
