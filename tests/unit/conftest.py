from __future__ import annotations
import typing
import pytest
from rest_framework.test import APIClient

if typing.TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rpi_controller.models import Sensor
    from django_webtest import DjangoTestApp


@pytest.fixture
def dummy_sensor() -> "Sensor":
    from test_utils.factories import SensorFactory
    return SensorFactory.create()


@pytest.fixture
def admin_user() -> "User":
    from test_utils.factories import SuperUserFactory
    return SuperUserFactory.create()


@pytest.fixture
def django_app_admin(django_app: "DjangoTestApp", admin_user: "User") -> "DjangoTestApp":
    django_app.set_user(admin_user)
    return django_app


@pytest.fixture
def django_api() -> APIClient:
    return APIClient()
