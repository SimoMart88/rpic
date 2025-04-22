import typing
import pytest
from django.urls import reverse

if typing.TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from _pytest.fixtures import TopRequest
    from pytest_django.fixtures import SettingsWrapper
    from rpi_controller.models import Device


@pytest.mark.django_db
def test_home(django_app: "DjangoTestApp") -> None:
    url_home: str = reverse("home")
    response = django_app.get(url_home)
    assert response.status_code == 200
    assert "Admin" in response.text


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_home_device(django_app: "DjangoTestApp", device_fixture_name: str, templates_for_testing: "SettingsWrapper",
                     request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    url_home: str = reverse("home")
    response = django_app.get(url_home)
    assert response.status_code == 200
    assert dummy_device.name not in response.text

    dummy_device.visible = True
    dummy_device.save()

    response = django_app.get(url_home)
    assert response.status_code == 200
    assert dummy_device.name in response.text
