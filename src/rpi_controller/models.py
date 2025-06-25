from __future__ import annotations

import json

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from strategy_field.fields import StrategyField

import typing
import logging

from rpi_controller.interfaces import Interface
from rpi_controller.interfaces.sensors.registry import sensor_registry
from rpi_controller.interfaces.actuators.registry import actuator_registry
from rpi_controller.interfaces.controllers.registry import controller_registry
from rpi_controller.interfaces.exceptions import InterfaceUpdateNotRequiredException, InterfaceException
from rpi_controller.exceptions import DeviceException, SensorException, ActuatorException, ControllerException
from rpi_controller.signals import post_device_control


logger = logging.getLogger(__name__)


class Device(models.Model):
    exception_class: typing.Type[DeviceException] = DeviceException

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
    last_status_update_time = models.DateTimeField(null=True, blank=True)
    last_status_update_log = models.TextField(null=True, blank=True)
    interface: typing.Optional[Interface] = None
    periodic_tasks = models.ManyToManyField("django_celery_beat.PeriodicTask", blank=True)

    def read_status(self) -> dict[typing.Any, typing.Any]:
        raise NotImplementedError("Status read not supported")

    def update_status(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        raise NotImplementedError("Status update not supported")

    def save(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def _as_json_value(self, value: typing.Any) -> typing.Any:
        return json.loads(json.dumps(value))

    def _set_success(self) -> None:
        self.last_status_update_time = timezone.now()
        self.last_status_update_log = f"{self.__class__.__name__} status updated successfully"
        self.last_update_status = self.UpdateStatus.SUCCESS
        self.save()

    def _set_failure(self, error_message: str) -> None:
        self.last_status_update_time = timezone.now()
        self.last_status_update_log = error_message
        self.last_update_status = self.UpdateStatus.FAILURE
        self.save()

    def _control_interface(
            self, interface_func_name: str, *args: typing.Any, **kwargs: typing.Any
    ) -> dict[typing.Any, typing.Any]:
        class_name = self.__class__.__name__
        try:
            logger.info("[%s '%s'] Control with input: '%s' + '%s'", class_name, self.slug, args, kwargs)
            self.status = self._as_json_value(getattr(self.interface, interface_func_name)(*args, **kwargs))
            logger.info("[%s '%s'] Control result: %s", class_name, self.slug, self.status)

            self._set_success()
        except InterfaceUpdateNotRequiredException:
            logger.info("[%s '%s'] Status update not required", class_name)
        except InterfaceException as ex:
            error_message = f"(Interface Error): {ex}"
            self._set_failure(error_message)
            raise self.exception_class(error_message)
        except Exception as ex:
            error_message = f"(Unexpected Error): {ex}"
            self._set_failure(error_message)
            raise self.exception_class(error_message)
        finally:
            post_device_control.send(sender=self.__class__, instance=self)

        return self.status

    def __str__(self) -> str:
        return self.name

    class Meta:
        abstract = True


class Sensor(Device):
    exception_class = SensorException

    interface = StrategyField(registry=sensor_registry)

    def read_status(self) -> dict[typing.Any, typing.Any]:
        return self._control_interface("read_input")


class Actuator(Device):
    exception_class = ActuatorException

    interface = StrategyField(registry=actuator_registry)

    def read_status(self) -> dict[typing.Any, typing.Any]:
        return self._control_interface("read_input")

    def update_status(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return self._control_interface("control", *args, **kwargs)


class Controller(Device):
    exception_class = ControllerException

    interface = StrategyField(registry=controller_registry)
    sensors = models.ManyToManyField(Sensor, through='ControlledSensorDetails', related_name="controllers")
    actuators = models.ManyToManyField(Actuator, through='ControlledActuatorDetails', related_name="controllers")

    def update_status(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return self._control_interface("control", *args, **kwargs)


class ControlledSensorDetails(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE)
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)
    config = models.JSONField(default=dict)


class ControlledActuatorDetails(models.Model):
    actuator = models.ForeignKey(Actuator, on_delete=models.CASCADE)
    controller = models.ForeignKey(Controller, on_delete=models.CASCADE)
    config = models.JSONField(default=dict)
