# Create your models here.

from django.db import models
from strategy_field.fields import StrategyField

from typing import Any, TYPE_CHECKING

from rpi_controller.core.interfaces.sensors import SensorRegistry

if TYPE_CHECKING:
    from strategy_field.registry import Registry


class Device(models.Model):
    _registry: "type[Registry] | None" = None

    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    visible = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)
    config = models.JSONField(default=dict)
    interface = StrategyField(registry=lambda model: model._registry)

    def use(self, *args: Any, **kwargs: Any) -> dict[Any, Any]:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Sensor(Device):
    _registry = SensorRegistry

    gpio_refs = models.JSONField(default=dict)

    def use(self, *args: Any, **kwargs: Any) -> dict[Any, Any]:
        return self.interface.read_input(self.gpio_refs, self.config)
