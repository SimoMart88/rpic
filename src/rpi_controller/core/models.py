# Create your models here.

from django.db import models
from strategy_field.fields import StrategyField

from typing import Any


class Device(models.Model):
    _registry = None

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
