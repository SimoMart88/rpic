import typing
from django.contrib import admin
from rpi_controller.models import Sensor


if typing.TYPE_CHECKING:
    from django.db import models


class DeviceAdmin(admin.ModelAdmin[models.Model]):
    list_display = ["name", "slug", "visible", "enabled", "interface"]
    list_filter = ["visible", "enabled", "interface"]
    readonly_fields = ["config"]


admin.site.register(Sensor, DeviceAdmin)
