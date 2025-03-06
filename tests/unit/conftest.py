from __future__ import annotations
import typing
import pytest
from rest_framework.test import APIClient
from strategy_field.utils import fqn

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rpi_controller.models import Sensor, Actuator
    from django_webtest import DjangoTestApp


@pytest.fixture
def dummy_sensor_update_not_required() -> "Sensor":
    from test_utils.factories import SensorFactory
    from rpi_controller.models import Sensor
    from test_utils.interfaces import DummyUpdateNotRequiredSensorInterface

    sensor = SensorFactory.create(
        status={"dummy_key": "dummy_value_no_update"},
        interface=fqn(DummyUpdateNotRequiredSensorInterface),
        last_status_update_log="Previous log",
        last_update_status=Sensor.UpdateStatus.SUCCESS
    )
    return sensor


@pytest.fixture
def dummy_sensor_error() -> "Sensor":
    from test_utils.factories import SensorFactory
    from test_utils.interfaces import DummyErrorSensorInterface

    sensor = SensorFactory.create(
        status={"dummy_key": "dummy_value"},
        interface=fqn(DummyErrorSensorInterface),
    )
    return sensor


@pytest.fixture
def dummy_actuator_error() -> "Actuator":
    from test_utils.factories import ActuatorFactory
    from test_utils.interfaces import DummyActuatorErrorInterface

    actuator = ActuatorFactory.create(
        status={"dummy_key": "dummy_value"},
        interface=fqn(DummyActuatorErrorInterface),
    )
    return actuator


@pytest.fixture
def django_app_admin(django_app: "DjangoTestApp", admin_user: "User") -> "DjangoTestApp":
    django_app.set_user(admin_user)
    return django_app


@pytest.fixture
def django_api() -> APIClient:
    return APIClient()
