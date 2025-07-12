import typing
import pytest
from unittest.mock import Mock
from datetime import timedelta
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.safestring import SafeString
from django_celery_beat.models import PeriodicTask
from django.utils.timezone import now
from django.utils.html import escape
from django.contrib.auth.models import User, Permission


if typing.TYPE_CHECKING:
    import types
    from django_webtest import DjangoTestApp
    from rpi_controller.models import Device
    from django.db.models.options import Options
    from pytest_django.fixtures import SettingsWrapper
    from _pytest.fixtures import TopRequest
    from pytest import MonkeyPatch


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
@pytest.mark.parametrize("url_name,url_extra,required_permission_type_name", [
    pytest.param("add_periodic_task", "?periodic_task_id=%(task_id)s", "change", id="add_periodic_task"),
    pytest.param("change_periodic_task", "?periodic_task_id=%(task_id)s", "change", id="change_periodic_task"),
    pytest.param("delete_periodic_task", "?periodic_task_id=%(task_id)s", "change", id="delete_periodic_task"),
    pytest.param("configure", "", "change", id="configure"),
    pytest.param("schedule", "", "change", id="schedule"),
    pytest.param("test", "", "view", id="test"),
    pytest.param("monitor", "", "view", id="monitor"),
])
def test_admin_extra_view_permission(request: "TopRequest", django_app: "DjangoTestApp", staff_user: User,
                                     device_fixture_name: str, dummy_periodic_task: "PeriodicTask",
                                     url_name: str, url_extra: str, required_permission_type_name: str,
                                     templates_for_testing: "SettingsWrapper") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    dummy_device.periodic_tasks.add(dummy_periodic_task)

    opts: "Options"["Device"] = dummy_device.__class__._meta
    target_url = (
        f'{reverse(admin_urlname(opts, SafeString(url_name)), args=[dummy_device.pk])}'
        f'{url_extra % {"task_id": dummy_periodic_task.id}}'
    )

    django_app.set_user(staff_user)

    response = django_app.get(target_url, expect_errors=True)
    assert response.status_code == 403

    permission = Permission.objects.get(
        codename=f"{required_permission_type_name}_{dummy_device._meta.model_name.lower()}"
    )
    staff_user.user_permissions.add(permission)

    response = django_app.get(target_url)
    assert response.status_code == 200



@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
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
    pytest.param("dummy_controller", id="controller"),
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
    pytest.param("dummy_controller", "[\"input_value\"]", "input_value", id="controller"),
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
    pytest.param("dummy_controller", id="controller"),
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
    pytest.param("dummy_controller_error", id="controller"),
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

@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_schedule_list(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                              request: "TopRequest", dummy_periodic_task: PeriodicTask) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert str(dummy_periodic_task) not in response.text

    url_configure: str = reverse(admin_urlname(opts, SafeString("schedule")), args=[dummy_device.pk])
    response = django_app_admin.get(url_configure)
    assert response.status_code == 200
    assert str(dummy_periodic_task) not in response.text

    dummy_device.periodic_tasks.add(dummy_periodic_task)

    response = django_app_admin.get(url_configure)
    add_url = f'{reverse(admin_urlname(opts, SafeString("add_periodic_task")), args=[dummy_device.pk])}'
    change_url = (f'{reverse(admin_urlname(opts, SafeString("change_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')
    delete_url = (f'{reverse(admin_urlname(opts, SafeString("delete_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')
    assert response.status_code == 200
    assert dummy_periodic_task.name in response.text
    assert f'<a href="{add_url}" class="addlink">Add</a>' in response.text
    assert f'<a href="{change_url}" class="changelink">Change</a>' in response.text
    assert f'<a href="{delete_url}" class="deletelink">Delete</a>' in response.text

    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert str(dummy_periodic_task) in response.text


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name,periodic_task_class_name", [
    pytest.param("dummy_sensor", "rpi_controller.tasks.sensor_read_status", id="sensor"),
    pytest.param("dummy_actuator", "rpi_controller.tasks.actuator_update_status_task", id="actuator"),
    pytest.param("dummy_controller", "rpi_controller.tasks.controller_update_status", id="controller"),
])
def test_device_schedule_add(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                             periodic_task_class_name: str, request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    assert dummy_device.periodic_tasks.count() == 0

    periodic_task_name: str = "periodic_task_name"

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert periodic_task_name not in response.text

    add_task_url = reverse(admin_urlname(opts, SafeString("add_periodic_task")), args=[dummy_device.pk])
    response = django_app_admin.get(add_task_url)
    form = response.forms["config-form"]

    assert response.status_code == 200
    assert "task_name" in form.fields
    assert "enabled" in form.fields
    assert "crontab_expression" in form.fields
    assert "update_kwargs" in form.fields

    form["task_name"] = periodic_task_name
    response = form.submit().follow()
    assert response.status_code == 302
    assert response.url == url_change

    assert dummy_device.periodic_tasks.count() == 1
    periodic_task = dummy_device.periodic_tasks.get(name=periodic_task_name)
    assert periodic_task.task == periodic_task_class_name

    response = response.follow()
    assert response.status_code == 200
    assert str(periodic_task) in response.text
    assert f'Configured periodic task {periodic_task_name}' in response.text


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_schedule_add_error(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                                   request: "TopRequest", monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    monkeypatch.setattr("rpi_controller.admin.HttpResponseRedirect", Mock(side_effect=Exception("ERROR")))
    periodic_task_name: str = "periodic_task_name"

    assert dummy_device.periodic_tasks.count() == 0

    add_task_url = reverse(admin_urlname(opts, SafeString("add_periodic_task")), args=[dummy_device.pk])
    response = django_app_admin.get(add_task_url)
    assert response.status_code == 200

    form = response.forms["config-form"]
    form["task_name"] = periodic_task_name
    response = form.submit()
    assert response.status_code == 200
    assert f'Configured periodic task {periodic_task_name} failure:' in response.text
    assert dummy_device.periodic_tasks.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_schedule_change(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                                request: "TopRequest", dummy_periodic_task: PeriodicTask) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    dummy_device.periodic_tasks.add(dummy_periodic_task)

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert str(dummy_periodic_task) in response.text

    change_url = (f'{reverse(admin_urlname(opts, SafeString("change_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')
    response = django_app_admin.get(change_url)
    form = response.forms["config-form"]

    assert response.status_code == 200
    assert "task_name" in form.fields
    assert "enabled" in form.fields
    assert "crontab_expression" in form.fields
    assert "update_kwargs" in form.fields

    new_periodic_task_name = "new_periodic_task_name"
    form["task_name"] = new_periodic_task_name
    response = form.submit().follow()
    assert response.status_code == 302
    assert response.url == url_change

    dummy_periodic_task.refresh_from_db()

    response = response.follow()
    assert response.status_code == 200
    assert str(dummy_periodic_task) in response.text
    assert f'Updated periodic task configuration {new_periodic_task_name}' in response.text


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_schedule_change_error(django_app_admin: "DjangoTestApp", device_fixture_name: str, request: "TopRequest",
                                      monkeypatch: pytest.MonkeyPatch, dummy_periodic_task: PeriodicTask) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    monkeypatch.setattr("rpi_controller.admin.HttpResponseRedirect", Mock(side_effect=Exception("ERROR")))

    dummy_device.periodic_tasks.add(dummy_periodic_task)

    change_url = (f'{reverse(admin_urlname(opts, SafeString("change_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')
    response = django_app_admin.get(change_url)
    assert response.status_code == 200

    form = response.forms["config-form"]
    new_periodic_task_name = "new_periodic_task_name"
    form["task_name"] = new_periodic_task_name
    response = form.submit()
    assert response.status_code == 200
    assert f'Periodic task {new_periodic_task_name} configuration failure:' in response.text
    dummy_periodic_task.refresh_from_db()
    assert dummy_periodic_task.name != new_periodic_task_name


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_schedule_delete(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                                request: "TopRequest", dummy_periodic_task: PeriodicTask) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    dummy_device.periodic_tasks.add(dummy_periodic_task)

    url_change: str = reverse(admin_urlname(opts, SafeString("change")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    assert str(dummy_periodic_task) in response.text

    change_url = (f'{reverse(admin_urlname(opts, SafeString("delete_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')
    response = django_app_admin.get(change_url)
    form = response.forms["config-form"]

    assert response.status_code == 200
    assert "confirm_operation" in form.fields

    form["confirm_operation"].checked =True
    response = form.submit().follow()
    assert response.status_code == 302
    assert response.url == url_change

    response = response.follow()
    assert response.status_code == 200
    assert str(dummy_periodic_task) not in response.text
    assert f'Deleted periodic task {dummy_periodic_task.name}' in response.text

    assert dummy_device.periodic_tasks.count() == 0


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_schedule_delete_error(django_app_admin: "DjangoTestApp", device_fixture_name: str, request: "TopRequest",
                                      monkeypatch: pytest.MonkeyPatch, dummy_periodic_task: PeriodicTask) -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    monkeypatch.setattr("rpi_controller.admin.HttpResponseRedirect", Mock(side_effect=Exception("ERROR")))

    dummy_device.periodic_tasks.add(dummy_periodic_task)

    change_url = (f'{reverse(admin_urlname(opts, SafeString("delete_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')
    response = django_app_admin.get(change_url)
    assert response.status_code == 200

    form = response.forms["config-form"]
    form["confirm_operation"].checked =True
    response = form.submit()
    assert response.status_code == 200
    assert f'Periodic task {dummy_periodic_task.name} deletion failure:' in response.text
    assert dummy_device.periodic_tasks.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_device_monitor(django_app_admin: "DjangoTestApp", device_fixture_name: str,
                        request: "TopRequest", system_monitor_mock: "types.ModuleType",
                        monkeypatch: "MonkeyPatch") -> None:
    monkeypatch.setattr("rpi_controller.admin.monitor", system_monitor_mock.monitor)
    monitor_fields = {"monitor_key": "monitor_value"}

    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    opts: "Options"["Device"] = dummy_device.__class__._meta

    system_monitor_mock.monitor.write_entry(key=dummy_device.slug, fields=monitor_fields)

    url_change: str = reverse(admin_urlname(opts, SafeString("monitor")), args=[dummy_device.pk])
    response = django_app_admin.get(url_change)
    assert response.status_code == 200
    form = response.forms["config-form"]
    assert "start_time_0" in form.fields
    assert "start_time_1" in form.fields
    assert "end_time_0" in form.fields
    assert "end_time_1" in form.fields

    form["end_time_0"] = (now() - timedelta(days=1)).date().isoformat()
    response = form.submit()
    assert response.status_code == 200
    assert escape(str(monitor_fields)) not in response.text

    form = response.forms["config-form"]
    form["end_time_0"] = (now() + timedelta(days=1)).date().isoformat()
    response = form.submit()
    assert response.status_code == 200
    assert escape(str(monitor_fields)) in response.text
