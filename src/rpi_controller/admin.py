import typing
from django.contrib import admin
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django.contrib.admin.helpers import AdminForm
from django.http.response import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse

from rpi_controller.models import Sensor

from admin_extra_buttons.decorators import button


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device
    from django.http.request import HttpRequest
    from django.http.response import HttpResponse
    from django.forms import Form


BLACK_ON_GREEN = 'background-color:#88FF88;color:black'


class DeviceAdmin(ExtraButtonsMixin, admin.ModelAdmin["Device"]):
    list_display = ["name", "slug", "visible", "enabled", "interface_label"]
    list_filter = ["visible", "enabled", "interface"]
    readonly_fields = ["config"]

    def get_object_or_404(self, request: "HttpRequest", pk: str) -> "Device":
        try:
            return self.get_object(request, pk)
        except Device.DoesNotExist:
            raise Http404

    @admin.display(description="Interface")
    def interface_label(self, obj: "Device") -> str:
        return str(obj.interface.label)

    @button(html_attrs={'style': BLACK_ON_GREEN})
    def configure(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj: "Device" = self.get_object_or_404(request, pk)
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Interface configuration")
        form_class: typing.Type[Form] = obj.interface.config_form

        if request.method == "POST":
            config_form = form_class(request.POST)
            if config_form.is_valid():
                obj.config = config_form.cleaned_data
                obj.save()
                self.message_user(request, "Configured interface {}".format(obj.name))
                return HttpResponseRedirect("..")
        else:
            config_form = form_class(initial={k: v for k, v in obj.config.items() if k in form_class.declared_fields})

        context["admin_form"] = AdminForm(
            config_form, [("", {"fields": form_class.declared_fields})], {}   # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/configure.html", context)


admin.site.register(Sensor, DeviceAdmin)
