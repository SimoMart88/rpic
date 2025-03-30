import typing
import pytest
from freezegun import freeze_time
from rest_framework.reverse import reverse


if typing.TYPE_CHECKING:
    from rest_framework.test import APIClient
    from rpi_controller.models import Device, Sensor, Actuator
    from _pytest.fixtures import TopRequest


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name,view_name", [
    pytest.param("dummy_sensor", "api-sensor-detail", id="sensor"),
    pytest.param("dummy_actuator", "api-actuator-detail", id="actuator"),
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
def test_sensor_api_read_status(django_api: "APIClient", dummy_sensor: "Sensor") -> None:
    url = reverse('api-sensor-read-status', args=[dummy_sensor.slug])

    response = django_api.post(url, {})

    assert response.data == {
        'name': dummy_sensor.name,
        'slug': dummy_sensor.slug,
        'visible': False,
        'status': {'dummy_key': 'dummy_value'},
        'interface': 'dummysensor',
        'last_status_update_time': '2000-01-01 00:00:00',
        'last_status_update_log': 'Sensor status updated successfully',
        'last_update_status': 'SUCCESS',
    }


@pytest.mark.django_db()
@freeze_time("2000-01-01 00:00:00")
def test_actuator_api_update_status(django_api: "APIClient", dummy_actuator: "Actuator") -> None:
    url = reverse('api-actuator-update-status', args=[dummy_actuator.slug])

    response = django_api.post(url, {"updated_key": "updated_value"})

    assert response.data == {
        'name': dummy_actuator.name,
        'slug': dummy_actuator.slug,
        'visible': False,
        'status': {'args': [], 'kwargs': {'updated_key': ['updated_value']}},
        'interface': 'dummyactuator',
        'last_status_update_time': '2000-01-01 00:00:00',
        'last_status_update_log': 'Actuator status updated successfully',
        'last_update_status': 'SUCCESS',
    }
