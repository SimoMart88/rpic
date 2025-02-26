import typing
import pytest
from freezegun import freeze_time
from rest_framework.reverse import reverse


if typing.TYPE_CHECKING:
    from rest_framework.test import APIClient
    from rpi_controller.models import Sensor


@pytest.mark.django_db()
def test_sensor_api_get(django_api: "APIClient", dummy_sensor: "Sensor") -> None:
    url = reverse('api-sensor-detail', args=[dummy_sensor.slug])

    response = django_api.get(url)

    assert response.data == {
        'name': dummy_sensor.name,
        'slug': dummy_sensor.slug,
        'visible': False,
        'status': {},
        'interface': 'dummysensor',
        'last_status_update_time': None,
        'last_status_update_log': None,
        'last_update_status': 'NEW',
    }


@pytest.mark.django_db()
@freeze_time("2000-01-01 00:00:00")
def test_sensor_api_use(django_api: "APIClient", dummy_sensor: "Sensor") -> None:
    url = reverse('api-sensor-read-status', args=[dummy_sensor.slug])

    response = django_api.post(url, {})

    assert response.data == {
        'name': dummy_sensor.name,
        'slug': dummy_sensor.slug,
        'visible': False,
        'status': {'dummy_key': 'dummy_value'},
        'interface': 'dummysensor',
        'last_status_update_time': '2000-01-01 01:00:00',
        'last_status_update_log': 'Sensor status updated successfully',
        'last_update_status': 'SUCCESS',
    }
