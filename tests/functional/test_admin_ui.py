import pytest
import typing
from django.urls import reverse
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.utils.safestring import SafeString
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


if typing.TYPE_CHECKING:
    from rpi_controller.models import Device
    from selenium.webdriver.remote.webdriver import WebDriver
    from pytest_django.live_server_helper import LiveServer
    from django_celery_beat.models import PeriodicTask
    from _pytest.fixtures import TopRequest
    from django.db.models.options import Options


@pytest.mark.selenium
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor", id="sensor"),
    pytest.param("dummy_actuator", id="actuator"),
    pytest.param("dummy_controller", id="controller"),
])
def test_admin_schedule_crontab_edit(selenium_logged_admin: "WebDriver", live_server: "LiveServer",
                                     device_fixture_name: str, dummy_periodic_task: "PeriodicTask",
                                     request: "TopRequest") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)
    dummy_device.periodic_tasks.add(dummy_periodic_task)

    opts: "Options"["Device"] = dummy_device.__class__._meta
    change_url = (f'{reverse(admin_urlname(opts, SafeString("change_periodic_task")), args=[dummy_device.pk])}'
                  f'?periodic_task_id={dummy_periodic_task.id}')

    selenium_logged_admin.get(f"{live_server.url}{change_url}")
    crontab_expression = selenium_logged_admin.find_element(By.ID, "id_crontab_expression")

    assert crontab_expression.get_attribute("value") == "*/5 * * * *"
    assert WebDriverWait(selenium_logged_admin, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "id_crontab_expression_helptext"),
            "Every 5 minutes"
        )
    )

    crontab_expression.click()
    crontab_expression.clear()
    crontab_expression.send_keys("0 1 2 3 4")

    assert WebDriverWait(selenium_logged_admin, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "id_crontab_expression_helptext"),
            "At 01:00 AM, on day 2 of the month, and on Thursday, only in March"
        )
    )
