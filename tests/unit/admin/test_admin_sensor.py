import typing
import pytest
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.safestring import SafeString

if typing.TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from rpi_controller.models import Sensor
    from django.db.models.options import Options


@pytest.mark.django_db
def test_sensor_change(django_app_admin: "DjangoTestApp", dummy_sensor: "Sensor") -> None:
    opts: "Options"["Sensor"] = dummy_sensor.__class__._meta

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_sensor.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert "config" not in response.forms["sensor_form"].fields

@pytest.mark.django_db
def test_sensor_configure(django_app_admin: "DjangoTestApp", dummy_sensor: "Sensor") -> None:
    opts: "Options"["Sensor"] = dummy_sensor.__class__._meta

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_sensor.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert "dummy_input" not in response.text

    url_configure: str = reverse(admin_urlname(opts, SafeString("configure")), args=[dummy_sensor.pk])
    response = django_app_admin.get(url_configure)
    form = response.forms["config-form"]

    assert response.status_code == 200
    assert "dummy_input" in form.fields

    form["dummy_input"] = "din"
    response = form.submit().follow()
    assert response.status_code == 302
    assert response.url == url_change

    response = response.follow()
    assert response.status_code == 200
    assert "dummy_input" in response.text
