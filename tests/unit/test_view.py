import typing
import pytest
from django.urls import reverse

if typing.TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from rpi_controller.models import Sensor
    from pytest_django.fixtures import SettingsWrapper


@pytest.mark.django_db
def test_home(django_app: "DjangoTestApp") -> None:
    url_home: str = reverse("home")
    response = django_app.get(url_home)
    assert response.status_code == 200
    assert "Admin" in response.text


@pytest.mark.django_db
def test_home_sensors(django_app: "DjangoTestApp", dummy_sensor: "Sensor", templates_for_testing: "SettingsWrapper") -> None:
    url_home: str = reverse("home")
    response = django_app.get(url_home)
    assert response.status_code == 200
    assert "Sensors" in response.text
    assert dummy_sensor.name not in response.text

    dummy_sensor.visible = True
    dummy_sensor.save()

    response = django_app.get(url_home)
    assert response.status_code == 200
    assert dummy_sensor.name in response.text
