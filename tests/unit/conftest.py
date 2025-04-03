from __future__ import annotations
import typing
import pytest
from rest_framework.test import APIClient
from strategy_field.utils import fqn

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rpi_controller.models import Sensor, Actuator, Controller
    from django_webtest import DjangoTestApp


@pytest.fixture
def django_app_admin(django_app: "DjangoTestApp", admin_user: "User") -> "DjangoTestApp":
    django_app.set_user(admin_user)
    return django_app


@pytest.fixture
def django_api() -> APIClient:
    return APIClient()



@pytest.fixture
def dummy_sensor_update_not_required() -> "Sensor":
    from test_utils.factories import SensorFactory
    from rpi_controller.models import Sensor
    from test_utils.interfaces import DummyUpdateNotRequiredSensorInterface

    return SensorFactory.create(
        status={"dummy_key": "dummy_value_no_update"},
        interface=fqn(DummyUpdateNotRequiredSensorInterface),
        last_status_update_log="Previous log",
        last_update_status=Sensor.UpdateStatus.SUCCESS
    )


@pytest.fixture
def dummy_sensor_error() -> "Sensor":
    from test_utils.factories import SensorFactory
    from test_utils.interfaces import DummyErrorSensorInterface

    return SensorFactory.create(
        status={"dummy_key": "dummy_value"},
        interface=fqn(DummyErrorSensorInterface),
    )


@pytest.fixture
def dummy_actuator_update_not_required() -> "Actuator":
    from test_utils.factories import ActuatorFactory
    from rpi_controller.models import Actuator
    from test_utils.interfaces import DummyUpdateNotRequiredActuatorInterface

    return ActuatorFactory.create(
        status={"dummy_key": "dummy_value_no_update"},
        interface=fqn(DummyUpdateNotRequiredActuatorInterface),
        last_status_update_log="Previous log",
        last_update_status=Actuator.UpdateStatus.SUCCESS
    )


@pytest.fixture
def dummy_actuator_error() -> "Actuator":
    from test_utils.factories import ActuatorFactory
    from test_utils.interfaces import DummyActuatorErrorInterface

    return ActuatorFactory.create(
        status={"dummy_key": "dummy_value"},
        interface=fqn(DummyActuatorErrorInterface),
    )


@pytest.fixture
def dummy_controller_update_not_required() -> "Controller":
    from test_utils.factories import ControllerFactory
    from rpi_controller.models import Controller
    from test_utils.interfaces import DummyUpdateNotRequiredControllerInterface

    return ControllerFactory.create(
        status={"dummy_key": "dummy_value_no_update"},
        interface=fqn(DummyUpdateNotRequiredControllerInterface),
        last_status_update_log="Previous log",
        last_update_status=Controller.UpdateStatus.SUCCESS
    )


@pytest.fixture
def dummy_controller_error() -> "Controller":
    from test_utils.factories import ControllerFactory
    from test_utils.interfaces import DummyControllerErrorInterface

    return ControllerFactory.create(
        status={"dummy_key": "dummy_value"},
        interface=fqn(DummyControllerErrorInterface),
    )
