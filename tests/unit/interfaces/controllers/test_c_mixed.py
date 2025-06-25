from __future__ import annotations
import pytest
import typing
from strategy_field.utils import fqn

from rpi_controller.interfaces.controllers.mixed import SensorTemperatureStepScaleFanControllerInterface
from rpi_controller.interfaces.exceptions import (InterfaceUserConfigurationException,
                                                  InterfaceConfigurationException,
                                                  InterfaceRuntimeException)
from test_utils.factories import ControlledSensorDetailsFactory, ControlledActuatorDetailsFactory
from test_utils.interfaces import DummySensorInterface, DummyActuatorInterface

if typing.TYPE_CHECKING:
    from rpi_controller.models import Controller


class DummyPrimarySensorInterface(DummySensorInterface):

    def read_input(self) -> dict[str, typing.Any]:
        return {"temperature": 25}


class DummySecondarySensorInterface(DummySensorInterface):

    def read_input(self) -> dict[str, typing.Any]:
        return {"temperature": 35}


class DummyFanActuatorInterface(DummyActuatorInterface):
    def control(self, *args: typing.Any, **kwargs: typing.Any) -> dict[typing.Any, typing.Any]:
        return kwargs


@pytest.fixture()
def working_controller(dummy_controller: "Controller") -> "Controller":
    dummy_controller.config["cooldown_period"] = 30
    dummy_controller.config["delta_temperature_step"] = 3

    ControlledSensorDetailsFactory(
        sensor__interface=fqn(DummyPrimarySensorInterface), controller=dummy_controller, config={"type": "primary"}
    )
    ControlledSensorDetailsFactory(
        sensor__interface=fqn(DummySecondarySensorInterface), controller=dummy_controller, config={"type": "secondary"}
    )
    ControlledActuatorDetailsFactory(
        actuator__interface=fqn(DummyFanActuatorInterface), controller=dummy_controller, config={"type": "primary"}
    )
    ControlledActuatorDetailsFactory(
        actuator__interface=fqn(DummyFanActuatorInterface), controller=dummy_controller, config={"type": "secondary"}
    )

    return dummy_controller



@pytest.mark.django_db()
def test_stssfc(working_controller: "Controller") -> None:
    controller_interface = SensorTemperatureStepScaleFanControllerInterface(working_controller)
    controller_output = controller_interface.control()
    assert controller_output['fan_primary'] is True
    assert controller_output['fan_secondary'] is True
    assert controller_output['delta_temperature'] == 10

    working_controller.refresh_from_db()
    for actuator in working_controller.actuators.all():
        assert actuator.status["active"] is True


@pytest.mark.django_db()
def test_stssfc_partial(working_controller: "Controller") -> None:
    working_controller.config["delta_temperature_step"] = 8

    controller_interface = SensorTemperatureStepScaleFanControllerInterface(working_controller)
    controller_output = controller_interface.control()
    assert controller_output['fan_primary'] is True
    assert controller_output['fan_secondary'] is False
    assert controller_output['delta_temperature'] == 10

    working_controller.refresh_from_db()
    primary_fan_actuator = working_controller.actuators.get(controlledactuatordetails__config__type="primary")
    assert primary_fan_actuator.status["active"] is True
    secondary_fan_actuator = working_controller.actuators.get(controlledactuatordetails__config__type="secondary")
    assert secondary_fan_actuator.status["active"] is False


@pytest.mark.django_db()
def test_stssfc_deactivate(working_controller: "Controller") -> None:
    working_controller.config["delta_temperature_step"] = 15
    primary_fan_actuator = working_controller.actuators.get(controlledactuatordetails__config__type="primary")
    primary_fan_actuator.status["active"] = True
    primary_fan_actuator.save()
    secondary_fan_actuator = working_controller.actuators.get(controlledactuatordetails__config__type="secondary")
    secondary_fan_actuator.status["active"] = False
    secondary_fan_actuator.save()

    controller_interface = SensorTemperatureStepScaleFanControllerInterface(working_controller)
    controller_output = controller_interface.control()
    assert controller_output['fan_primary'] is False
    assert controller_output['fan_secondary'] is False
    assert controller_output['delta_temperature'] == 10

    working_controller.refresh_from_db()
    primary_fan_actuator = working_controller.actuators.get(controlledactuatordetails__config__type="primary")
    assert primary_fan_actuator.status["active"] is False
    secondary_fan_actuator = working_controller.actuators.get(controlledactuatordetails__config__type="secondary")
    assert secondary_fan_actuator.status["active"] is False


@pytest.mark.django_db()
def test_stssfc_userconfig_error(dummy_controller: "Controller") -> None:
    with pytest.raises(InterfaceUserConfigurationException, match="'cooldown_period' not defined in config"):
        controller_interface = SensorTemperatureStepScaleFanControllerInterface(dummy_controller)
        controller_interface.control()


@pytest.mark.django_db()
def test_stssfc_interfaceconfig_error(dummy_controller: "Controller") -> None:
    dummy_controller.config["cooldown_period"] = 30
    dummy_controller.config["delta_temperature_step"] = 5

    with pytest.raises(InterfaceConfigurationException,
                       match="Missing required relation: Sensor matching query does not exist."):
        controller_interface = SensorTemperatureStepScaleFanControllerInterface(dummy_controller)
        controller_interface.control()


@pytest.mark.django_db()
def test_stssfc_interface_error(working_controller: "Controller") -> None:
    working_controller.config["delta_temperature_step"] = "WRONG"

    with pytest.raises(InterfaceRuntimeException, match='Fan controller unexpected error'):
        controller_interface = SensorTemperatureStepScaleFanControllerInterface(working_controller)
        controller_interface.control()
