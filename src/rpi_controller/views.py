import typing
from django.urls import reverse

from django.views.generic.base import TemplateView

from rpi_controller.models import Sensor, Actuator


class HomePageView(TemplateView):
    template_name = "rpi_controller/home.html"

    def get_context_data(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        context: dict[str, typing.Any] = super().get_context_data(**kwargs)
        context["nav_links"] = [
            {"name": "Admin", "url": reverse("admin:index")},
        ]
        context["sensors"] = Sensor.objects.filter(visible=True)
        context["actuators"] = Actuator.objects.filter(visible=True)
        return context
