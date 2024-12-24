from django.contrib import admin
from rpi_controller.models import Sensor, Device


class DeviceAdmin(admin.ModelAdmin[Device]):
    list_display = ["name", "slug", "visible", "enabled", "interface"]
    list_filter = ["visible", "enabled", "interface"]
    readonly_fields = ["config"]


admin.site.register(Sensor, DeviceAdmin)
