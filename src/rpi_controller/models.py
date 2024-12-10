# Create your models here.
from __future__ import annotations

from django.db import models
from strategy_field.fields import StrategyField

import typing

from rpi_controller.interfaces.sensors import sensor_registry

if typing.TYPE_CHECKING:
    from strategy_field.registry import Registry
    from rpi_controller.interfaces.sensors import SensorRegistry


class Device(models.Model):
    _registry: Registry | None = None

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    visible = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    interface = StrategyField(registry=lambda model: model._registry)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Sensor(Device):
    _registry: SensorRegistry = sensor_registry

    gpio_refs = models.JSONField(default=dict)

    def use(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return self.interface.read_input(self.gpio_refs, self.config)
