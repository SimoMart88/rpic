import logging
import typing

from django import forms
from django.core.exceptions import ObjectDoesNotExist

from rpi_controller.interfaces.controllers.base import ControllerInterface
from rpi_controller.interfaces.exceptions import InterfaceRuntimeException, InterfaceConfigurationException, \
    InterfaceUserConfigurationException
from rpi_controller.interfaces.forms import ConfigForm
from rpi_controller.interfaces.utils import is_status_update_required

from rpi_controller.models import Sensor, Actuator, ControlledSensorDetails, ControlledActuatorDetails


logger = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from rpi_controller.models import Controller


class SensorTemperatureStepScaleFanControllerForm(ConfigForm):

    delta_temperature_step = forms.IntegerField(label="Delta Temperature Step to enable/disable a Fan")
    cooldown_period = forms.IntegerField(label="Cooldown Period in seconds to enable/disable a Fan")
    primary_temperature_sensor = forms.ModelChoiceField(queryset=Sensor.objects.all())
    secondary_temperature_sensor = forms.ModelChoiceField(queryset=Sensor.objects.all())
    primary_fan_actuator = forms.ModelChoiceField(queryset=Actuator.objects.all())
    secondary_fan_actuator = forms.ModelChoiceField(queryset=Actuator.objects.all())

    def __init__(self, *args: typing.Any, instance: "Controller", **kwargs: typing.Any) -> None:
        if instance.sensors.count() == 2 and instance.actuators.count() == 2:
            kwargs["initial"] = {
                'primary_temperature_sensor': instance.sensors.get(controlledsensordetails__config__type="primary").pk,
                'secondary_temperature_sensor': instance.sensors.get(controlledsensordetails__config__type="secondary").pk,
                'primary_fan_actuator': instance.actuators.get(controlledactuatordetails__config__type="primary").pk,
                'secondary_fan_actuator': instance.actuators.get(controlledactuatordetails__config__type="primary").pk,
            }
        super().__init__(*args, instance=instance, **kwargs)

    def save(self) -> None:
        # Save sensors relationship
        self.instance.sensors.clear()
        ControlledSensorDetails.objects.create(
            sensor = self.cleaned_data.pop("primary_temperature_sensor"),
            controller = self.instance,
            config = {"type": "primary"}
        )
        ControlledSensorDetails.objects.create(
            sensor = self.cleaned_data.pop("secondary_temperature_sensor"),
            controller = self.instance,
            config = {"type": "secondary"}
        )

        # Save actuators relationship
        self.instance.actuators.clear()
        ControlledActuatorDetails.objects.create(
            actuator=self.cleaned_data.pop("primary_fan_actuator"),
            controller=self.instance,
            config={"type": "primary"}
        )
        ControlledActuatorDetails.objects.create(
            actuator=self.cleaned_data.pop("secondary_fan_actuator"),
            controller=self.instance,
            config={"type": "secondary"}
        )

        # Save config
        super().save()


class SensorTemperatureStepScaleFanControllerInterface(ControllerInterface):

    label = "Step Scale Fan on Temperature delta"
    config_form = SensorTemperatureStepScaleFanControllerForm
    template_name = "rpi_controller/interfaces/controller/stssfc.html"

    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        try:
            cooldown_period = self.context.config["cooldown_period"]

            is_status_update_required(self.context, self.context.last_status_update_time, cooldown_period)

            delta_temperature_step = self.context.config["delta_temperature_step"]
            primary_temperature_sensor = self.context.sensors.get(controlledsensordetails__config__type="primary")
            secondary_temperature_sensor = self.context.sensors.get(controlledsensordetails__config__type="secondary")
            primary_fan_actuator = self.context.actuators.get(controlledactuatordetails__config__type="primary")
            secondary_fan_actuator = self.context.actuators.get(controlledactuatordetails__config__type="secondary")
        except KeyError as e:
            raise InterfaceUserConfigurationException(f"{e} not defined in config")
        except ObjectDoesNotExist as e:
            raise InterfaceConfigurationException(f"Missing required relation: {e}")

        try:
            logger.info("[Controller '%s'] Checking sensor temperature", self.context.slug)
            primary_temperature = primary_temperature_sensor.read_status()["temperature"]
            secondary_temperature = secondary_temperature_sensor.read_status()["temperature"]
            logger.info("[Controller '%s'] Primary sensor temperature: %s | Secondary sensor temperature: %s",
                        self.context.slug, primary_temperature, secondary_temperature)

            logger.info("[Controller '%s'] Checking fan actuator status", self.context.slug)
            primary_fan_active = primary_fan_actuator.status.get("active")
            secondary_fan_active = secondary_fan_actuator.status.get("active")
            logger.info("[Controller '%s'] Primary fan actuator active: %s | Secondary fan actuator active: %s",
                        self.context.slug, primary_fan_active, secondary_fan_active)

            status = {"primary": primary_fan_active, "secondary": secondary_fan_active}

            target_status_update = {
                "primary": (delta_temperature_step, primary_fan_actuator),
                "secondary": (delta_temperature_step * 2, secondary_fan_actuator)
            }

            for fan_label, (delta_temperature, fan_actuator) in target_status_update.items():
                sensor_delta_temperature = secondary_temperature - delta_temperature
                if sensor_delta_temperature > primary_temperature:
                    logger.info("[Controller '%s'] Activating %s fan (%s > %s)",
                                self.context.slug, fan_label, delta_temperature, primary_temperature)
                    fan_actuator.update_status(active=True)
                    status[fan_label] = True
                else:
                    logger.info("[Controller '%s'] Deactivating %s fan (%s > %s)",
                                self.context.slug, fan_label, delta_temperature, primary_temperature)
                    fan_actuator.update_status(active=False)
                    status[fan_label] = False

            return status

        except Exception as e:
            logger.info("[Controller '%s'] Unexpected error: %s", self.context.slug, e)
            raise InterfaceRuntimeException('Fan controller unexpected error') from e
