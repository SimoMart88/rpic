import json
import typing

from django.conf import settings
from django.contrib import admin, messages
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.admin.helpers import AdminForm
from django.http.response import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse
from django.db import transaction
from django_celery_beat.models import (
    PeriodicTask,
    CrontabSchedule,
    IntervalSchedule,
    SolarSchedule,
    ClockedSchedule,
)

from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.models import Sensor, Actuator, Controller

from admin_extra_buttons.decorators import button, view


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse
    from django.forms import Form


BLACK_ON_GREEN = 'background-color:#88FF88;color:black'
BLACK_ON_YELLOW = 'background-color:#FFFF66;color:black'


def is_args(value: typing.Any) -> bool:
    if not isinstance(value, list):
        raise ValidationError("Argument must be a list")

    return True


def is_kwargs(value: typing.Any) -> bool:
    if not isinstance(value, dict):
        raise ValidationError("Keyword argument must be a dictionary")

    return True


class TestForm(forms.Form):
    input_args = forms.JSONField(required=False, initial=[], validators=[is_args])
    input_kwargs = forms.JSONField(required=False, initial={}, validators=[is_kwargs])


class SimplifiedPeriodicTaskForm(forms.Form):
    task_name = forms.CharField(max_length=255)
    enabled = forms.BooleanField(initial=True, required=False)
    crontab_expression = forms.CharField(initial="*/5 * * * *", max_length=255)
    update_kwargs = forms.JSONField(required=False, initial={}, validators=[is_kwargs])


class ConfirmationForm(forms.Form):
    confirm_operation = forms.BooleanField(initial=False, required=True)


class DeviceAdmin(ExtraButtonsMixin, admin.ModelAdmin["Device"]):
    list_display = ["name", "slug", "visible", "interface_label"]
    list_filter = ["visible", "interface"]
    readonly_fields = ["config", "status", "periodic_tasks",
                       "last_update_status", "last_status_update_time", "last_status_update_log"]
    periodic_task_form_class = SimplifiedPeriodicTaskForm
    periodic_task_name: typing.Optional[str] = None

    def get_object_or_404(self, request: "HttpRequest", pk: str) -> "Device":
        device: typing.Optional["Device"] = self.get_object(request, pk)

        if not device:
            raise Http404

        return device

    def run_test(self, device: "Device", *args: typing.Any, **kwargs: typing.Any) -> None:
        raise NotImplementedError

    @view(permission="add")
    def add_periodic_task(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        device: "Device" = self.get_object_or_404(request, pk)
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="New periodic task configuration")

        if request.method == "POST":
            periodic_task_form = self.periodic_task_form_class(request.POST)
            if periodic_task_form.is_valid():
                try:
                    with transaction.atomic():
                        minute, hour, day_of_week, month_of_year, day_of_month = periodic_task_form.cleaned_data["crontab_expression"].split(" ")
                        crontab, _ = CrontabSchedule.objects.get_or_create(
                            minute=minute, hour=hour, day_of_week=day_of_week,
                            month_of_year=month_of_year, day_of_month=day_of_month,
                            timezone=settings.TIME_ZONE,
                        )
                        periodic_task = PeriodicTask.objects.create(
                            name=periodic_task_form.cleaned_data["task_name"],
                            enabled=periodic_task_form.cleaned_data["enabled"],
                            task=self.periodic_task_name,
                            crontab=crontab,
                            args=json.dumps([device.slug]),
                            kwargs=json.dumps(periodic_task_form.cleaned_data["update_kwargs"]),
                        )
                        device.periodic_tasks.add(periodic_task)
                        self.message_user(request, "Configured periodic task {}".format(periodic_task.name))
                        return HttpResponseRedirect("..")
                except Exception as ex:
                    self.message_user(request, "Configured periodic task {} failure: {}".format(
                        periodic_task_form.cleaned_data["task_name"], str(ex)), messages.ERROR)
        else:
            periodic_task_form = self.periodic_task_form_class()

        context["admin_form"] = AdminForm(
            periodic_task_form, [("", {"fields": self.periodic_task_form_class.base_fields})], {}  # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/schedule_details.html", context)

    @view(permission="change")
    def change_periodic_task(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        device: "Device" = self.get_object_or_404(request, pk)
        periodic_task: "PeriodicTask" = device.periodic_tasks.get(id=request.GET["periodic_task_id"])
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Update periodic task configuration")

        if request.method == "POST":
            periodic_task_form = self.periodic_task_form_class(request.POST)
            if periodic_task_form.is_valid():
                try:
                    with transaction.atomic():
                        minute, hour, day_of_week, month_of_year, day_of_month = periodic_task_form.cleaned_data["crontab_expression"].split(" ")
                        crontab, _ = CrontabSchedule.objects.get_or_create(
                            minute=minute, hour=hour, day_of_week=day_of_week,
                            month_of_year=month_of_year, day_of_month=day_of_month,
                            timezone=settings.TIME_ZONE,
                        )

                        periodic_task.name = periodic_task_form.cleaned_data["task_name"]
                        periodic_task.enabled = periodic_task_form.cleaned_data["enabled"]
                        periodic_task.kwargs = json.dumps(periodic_task_form.cleaned_data["update_kwargs"])
                        periodic_task.crontab = crontab
                        periodic_task.save()

                        self.message_user(request, "Updated periodic task configuration {}".format(periodic_task.name))
                        return HttpResponseRedirect("..")
                except Exception as ex:
                    self.message_user(request, "Periodic task {} configuration failure: {}".format(
                        periodic_task_form.cleaned_data["task_name"], str(ex)), messages.ERROR)
        else:
            periodic_task_form = self.periodic_task_form_class(
                initial={
                    "task_name": periodic_task.name,
                    "enabled": periodic_task.enabled,
                    "crontab_expression": " ".join(str(periodic_task.crontab).split(" ", 5)[:5]),
                    "kwargs": periodic_task.kwargs,
                }
            )

        context["admin_form"] = AdminForm(
            periodic_task_form, [("", {"fields": self.periodic_task_form_class.base_fields})], {}  # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/schedule_details.html", context)

    @view(permission="delete")
    def delete_periodic_task(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        device: "Device" = self.get_object_or_404(request, pk)
        periodic_task: "PeriodicTask" = device.periodic_tasks.get(id=request.GET["periodic_task_id"])
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Delete periodic task configuration")

        if request.method == "POST":
            confirmation_form = ConfirmationForm(request.POST)
            if confirmation_form.is_valid():
                try:
                    with transaction.atomic():
                        device.periodic_tasks.remove(periodic_task)
                        periodic_task.delete()
                        self.message_user(request, "Deleted periodic task {}".format(periodic_task.name))
                        return HttpResponseRedirect("..")
                except Exception as ex:
                    self.message_user(request, "Periodic task {} deletion failure: {}".format(
                        periodic_task.name, str(ex)), messages.ERROR)
        else:
            confirmation_form = ConfirmationForm()

        context["admin_form"] = AdminForm(
            confirmation_form, [("", {"fields": ConfirmationForm.base_fields})], {} # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/input_form.html", context)

    @admin.display(description="Interface")
    def interface_label(self, device: "Device") -> str:
        return str(device.interface.label)

    @button(html_attrs={'style': BLACK_ON_GREEN})
    def configure(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        device: "Device" = self.get_object_or_404(request, pk)
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Interface configuration")
        form_class: typing.Type[ConfigForm] = device.interface.config_form

        if request.method == "POST":
            config_form = form_class(request.POST, instance=device)
            if config_form.is_valid():
                config_form.save()
                self.message_user(request, "Configured interface {}".format(device.name))
                return HttpResponseRedirect("..")
        else:
            config_form = form_class(
                initial={k: v for k, v in device.config.items() if k in form_class.base_fields},
                instance=device
            )

        context["admin_form"] = AdminForm(
            config_form, [("", {"fields": form_class.base_fields})], {}   # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/configure.html", context)

    @button(html_attrs={'style': BLACK_ON_GREEN})
    def schedule(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        device: "Device" = self.get_object_or_404(request, pk)
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Periodic task configuration")
        context["device"] = device
        context["device_class_name"] = device.__class__.__name__.lower()
        return TemplateResponse(request, "admin/device/schedule_list.html", context)

    @button(html_attrs={'style': BLACK_ON_YELLOW})
    def test(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        device: "Device" = self.get_object_or_404(request, pk)
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Interface test")
        form_class: typing.Type[Form] = TestForm
        context["device"]: typing.Type["Device"] = device

        if request.method == "POST":
            config_form = form_class(request.POST)
            if config_form.is_valid():
                try:
                    self.run_test(device, *config_form.cleaned_data["input_args"], **config_form.cleaned_data["input_kwargs"])
                    self.message_user(request, "Tested interface {} successfully".format(device.name))
                except Exception as ex:
                    self.message_user(request, "Tested interface {} failure: {}".format(
                        device.name, str(ex)), messages.ERROR)
        else:
            config_form = form_class(initial={k: v for k, v in device.config.items() if k in form_class.base_fields})

        context["admin_form"] = AdminForm(
            config_form, [("", {"fields": form_class.base_fields})], {}   # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/test.html", context)


class SensorAdmin(DeviceAdmin):
    periodic_task_name = "rpi_controller.tasks.sensor_read_status"

    def run_test(self, device: "Device", *args: typing.Any, **kwargs: typing.Any) -> None:
        device.read_status()


class ActuatorAdmin(DeviceAdmin):
    periodic_task_name = "rpi_controller.tasks.actuator_update_status_task"

    def run_test(self, device: "Device", *args: typing.Any, **kwargs: typing.Any) -> None:
        device.update_status(*args, **kwargs)


class ControllerAdmin(DeviceAdmin):
    readonly_fields = DeviceAdmin.readonly_fields + ["sensors", "actuators"]
    periodic_task_name = "rpi_controller.tasks.controller_control"

    def run_test(self, device: "Device", *args: typing.Any, **kwargs: typing.Any) -> None:
        device.update_status(*args, **kwargs)


admin.site.register(Sensor, SensorAdmin)
admin.site.register(Actuator, ActuatorAdmin)
admin.site.register(Controller, ControllerAdmin)


# Unregister django_celery_beat, simplified UI will be used
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
