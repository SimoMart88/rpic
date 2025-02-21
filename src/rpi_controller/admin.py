import typing
from django.contrib import admin, messages
from admin_extra_buttons.mixins import ExtraButtonsMixin
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.admin.helpers import AdminForm
from django.http.response import HttpResponseRedirect, Http404
from django.template.response import TemplateResponse

from rpi_controller.models import Sensor, Actuator

from admin_extra_buttons.decorators import button


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


class DeviceAdmin(ExtraButtonsMixin, admin.ModelAdmin["Device"]):
    list_display = ["name", "slug", "visible", "interface_label"]
    list_filter = ["visible", "interface"]
    readonly_fields = ["config", "status", "last_update_status", "last_status_update_time", "last_status_update_log"]

    def get_object_or_404(self, request: "HttpRequest", pk: str) -> "Device":
        obj = self.get_object(request, pk)

        if not obj:
            raise Http404

        return obj

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

    @button(html_attrs={'style': BLACK_ON_YELLOW})
    def test(self, request: "HttpRequest", pk: str) -> "HttpResponse":
        obj: "Device" = self.get_object_or_404(request, pk)
        context: dict[str, typing.Any] = self.get_common_context(request, pk, title="Interface test")
        form_class: typing.Type[Form] = TestForm
        context["device"]: "Device" = obj

        if request.method == "POST":
            config_form = form_class(request.POST)
            if config_form.is_valid():
                try:
                    obj.use(
                        *config_form.cleaned_data["input_args"], **config_form.cleaned_data["input_kwargs"]
                    )
                    if obj.last_update_status == obj.UpdateStatus.SUCCESS:
                        self.message_user(request, "Tested interface {} successfully".format(obj.name))
                    else:
                        self.message_user(request, "Tested interface {} failure: {}".format(
                            obj.name, obj.last_status_update_log), messages.ERROR)
                except Exception as ex:
                    self.message_user(request, str(ex), messages.ERROR)
        else:
            config_form = form_class(initial={k: v for k, v in obj.config.items() if k in form_class.declared_fields})

        context["admin_form"] = AdminForm(
            config_form, [("", {"fields": form_class.declared_fields})], {}   # type: ignore[arg-type, dict-item]
        )
        return TemplateResponse(request, "admin/device/test.html", context)


admin.site.register(Sensor, DeviceAdmin)
admin.site.register(Actuator, DeviceAdmin)
