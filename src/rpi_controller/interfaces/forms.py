import typing

from django import forms


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device


class ConfigForm(forms.Form):

    def __init__(self, *args: typing.Any, instance: "Device", **kwargs: typing.Any):
        super().__init__(*args, **kwargs)

        self.instance = instance

    def save(self) -> None:
        self.instance.config = self.cleaned_data  # type: ignore[assignment]
        self.instance.save()
