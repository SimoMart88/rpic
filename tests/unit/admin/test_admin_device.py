import typing
import pytest
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.safestring import SafeString

if typing.TYPE_CHECKING:
    from django_webtest import DjangoTestApp
    from rpi_controller.models import Device
    from django.db.models.options import Options
    from pytest_django.fixtures import SettingsWrapper
    from _pytest.fixtures import TopRequest


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
])
def test_device_change(django_app_admin: "DjangoTestApp", device_fixture_name: str, request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert "config" not in response.forms[f"{dummy_device.__class__.__name__.lower()}_form"].fields


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
])
def test_device_configure(django_app_admin: "DjangoTestApp", device_fixture_name: str, request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert "dummy_input" not in response.text

    url_configure: str = reverse(admin_urlname(opts, SafeString("configure")), args=[dummy_device.pk])
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


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name,test_input,test_output", [
    pytest.param("dummy_sensor", "[]", "dummy_value", id="sensor"),
    pytest.param("dummy_actuator", "[\"input_value\"]", "input_value", id="actuator"),
])
def test_device_test(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                     test_input: str, test_output: str, templates_for_testing: "SettingsWrapper",
                     request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    url_test: str = reverse(admin_urlname(opts, SafeString("test")), args=[dummy_device.pk])
    response = django_app_admin.get(url_test)
    form = response.forms["config-form"]

    assert response.status_code == 200
    assert "input_args" in form.fields
    assert "input_kwargs" in form.fields
    assert test_output not in response.text

    form["input_args"] = test_input
    response = form.submit()

    assert response.status_code == 200
    assert "Tested interface {} successfully".format(dummy_device.name) in response.text
    assert test_output in response.text


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
])
def test_device_test_input_error(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                                 templates_for_testing: "SettingsWrapper", request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    url_test: str = reverse(admin_urlname(opts, SafeString("test")), args=[dummy_device.pk])
    response = django_app_admin.get(url_test)
    form = response.forms["config-form"]

    assert response.status_code == 200
    form["input_args"] = '{"input": "ERROR"}'
    form["input_kwargs"] = '["ERROR"]'

    response = form.submit()
    assert "Argument must be a list" in response.text
    assert "Keyword argument must be a dictionary" in response.text


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor_error", id="sensor"),
    pytest.param("dummy_actuator_error", id="actuator"),
])
def test_device_test_error(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                                 templates_for_testing: "SettingsWrapper", request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    url_test: str = reverse(admin_urlname(opts, SafeString("test")), args=[dummy_device.pk])
    response = django_app_admin.get(url_test)
    form = response.forms["config-form"]
    response = form.submit()

    assert "Tested interface {} failure: {}".format(
        dummy_device.name, f"(Interface Error): {dummy_device.__class__.__name__} error"
    ) in response.text
