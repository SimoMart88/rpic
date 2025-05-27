import logging
import typing

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from rpi_controller.interfaces.controllers.base import ControllerInterface
from rpi_controller.interfaces.exceptions import InterfaceConfigurationException, \
    InterfaceUserConfigurationException
from rpi_controller.interfaces.forms import ConfigForm

from rpi_controller.models import Sensor, Actuator, ControlledSensorDetails, ControlledActuatorDetails


logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device


class MockControllerForm(ConfigForm):

    module_number = forms.IntegerField(label="Number used to calculate the sensor module")
    input_sensor = forms.ModelChoiceField(queryset=Sensor.objects.all())
    output_actuator = forms.ModelChoiceField(queryset=Actuator.objects.all())

    def __init__(self, *args: typing.Any, instance: "Device", **kwargs: typing.Any) -> None:
        if kwargs.get("initial") and (instance.sensors.count() == 1 and instance.actuators.count() == 1):
            kwargs["initial"].update({
                'input_sensor': instance.sensors.get(controlledsensordetails__config__type="input").pk,
                'output_actuator': instance.actuators.get(controlledactuatordetails__config__type="output").pk,
            })
        super().__init__(*args, instance=instance, **kwargs)

    def save(self) -> None:
        # Save sensor relation
        self.instance.sensors.clear()
        ControlledSensorDetails.objects.create(
            sensor = self.cleaned_data.pop("input_sensor"),
            controller = self.instance,
            config = {"type": "input"}
        )

        # Save actuator relation
        self.instance.actuators.clear()
        ControlledActuatorDetails.objects.create(
            actuator=self.cleaned_data.pop("output_actuator"),
            controller=self.instance,
            config={"type": "output"}
        )

        # Save config
        super().save()


class MockControllerInterface(ControllerInterface):

    label = "MockController"
    config_form = MockControllerForm
    template_name = "rpi_controller/interfaces/controllers/mock.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            module_number = self.context.config["module_number"]

            input_sensor = self.context.sensors.get(controlledsensordetails__config__type="input")
            output_actuator = self.context.actuators.get(controlledactuatordetails__config__type="output")
        except KeyError as e:
            raise InterfaceUserConfigurationException(f"{e} not defined in config")
        except ObjectDoesNotExist as e:
            raise InterfaceConfigurationException(f"Missing required relation: {e}")

        counter = input_sensor.read_status()["counter"]

        status = {}

        if counter % module_number == 0:
            output_actuator.update_status(flag=True)
            status["flag"] = True
        else:
            output_actuator.update_status(flag=False)
            status["flag"] = False

        return status
