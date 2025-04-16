import typing
import pytest
from freezegun import freeze_time
from rest_framework.reverse import reverse


if typing.TYPE_CHECKING:
    from rest_framework.test import APIClient
    from rpi_controller.models import Device
    from _pytest.fixtures import TopRequest


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name,view_name", [
    pytest.param("dummy_sensor", "api-sensor-detail", id="sensor"),
    pytest.param("dummy_actuator", "api-actuator-detail", id="actuator"),
    pytest.param("dummy_controller", "api-controller-detail", id="controller"),
])
def test_device_api_get(django_api: "APIClient", device_fixture_name: str, view_name: str,
                        request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    url = reverse(view_name, args=[dummy_device.slug])

    response = django_api.get(url)

    assert response.data == {
        'name': dummy_device.name,
        'slug': dummy_device.slug,
        'visible': False,
        'status': {},
        'interface': dummy_device._meta.get_field("interface").registry.get_name(dummy_device.interface),
        'last_status_update_time': None,
        'last_status_update_log': None,
        'last_update_status': 'NEW',
    }


@pytest.mark.django_db()
@freeze_time("2000-01-01 00:00:00")
@pytest.mark.parametrize("device_fixture_name,view_name", [
    pytest.param("dummy_sensor", "api-sensor-read-status", id="sensor"),
])
def test_sensor_api_read_status(django_api: "APIClient", device_fixture_name: str, view_name: str,
                                request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    url = reverse(view_name, args=[dummy_device.slug])

    response = django_api.post(url, {})

    assert response.data == {
        'name': dummy_device.name,
        'slug': dummy_device.slug,
        'visible': False,
        'status': {'dummy_key': 'dummy_value'},
        'interface': dummy_device._meta.get_field("interface").registry.get_name(dummy_device.interface),
        'last_status_update_time': '2000-01-01 00:00:00',
        'last_status_update_log': f'{dummy_device.__class__.__name__} status updated successfully',
        'last_update_status': 'SUCCESS',
    }


@pytest.mark.django_db()
@freeze_time("2000-01-01 00:00:00")
@pytest.mark.parametrize("device_fixture_name,view_name", [
    pytest.param("dummy_actuator", "api-actuator-update-status", id="actuator"),
    pytest.param("dummy_controller", "api-controller-update-status", id="controller"),
])
def test_actuator_api_update_status(django_api: "APIClient", device_fixture_name: str, view_name: str,
                                    request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    url = reverse(view_name, args=[dummy_device.slug])

    response = django_api.post(url, {"updated_key": "updated_value"})

    assert response.data == {
        'name': dummy_device.name,
        'slug': dummy_device.slug,
        'visible': False,
        'status': {'args': [], 'kwargs': {'updated_key': ['updated_value']}},
        'interface': dummy_device._meta.get_field("interface").registry.get_name(dummy_device.interface),
        'last_status_update_time': '2000-01-01 00:00:00',
        'last_status_update_log': f'{dummy_device.__class__.__name__} status updated successfully',
        'last_update_status': 'SUCCESS',
    }
