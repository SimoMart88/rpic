from django.contrib import admin
from rpi_controller.models import Sensor, Device


class DeviceAdmin(admin.ModelAdmin[Device]):
    list_display = ["name", "slug", "visible", "enabled", "interface_label"]
    list_filter = ["visible", "enabled", "interface"]
    readonly_fields = ["config"]

    @admin.display(description="Interface")
    def interface_label(self, obj: Device) -> str:
        return str(obj.interface.label)

admin.site.register(Sensor, DeviceAdmin)
