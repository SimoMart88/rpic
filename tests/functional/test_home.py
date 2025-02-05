import pytest
import typing
from strategy_field.utils import fqn
from freezegun import freeze_time
from datetime import datetime
from django.utils.timezone import localtime, now
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


if typing.TYPE_CHECKING:
    from rpi_controller.models import Sensor
    from pytest_django.fixtures import SettingsWrapper
    from selenium.webdriver.remote.webdriver import WebDriver
    from pytest_django.live_server_helper import LiveServer


@pytest.fixture
def dummy_sensor_ui(dummy_sensor: "Sensor") -> "Sensor":
    from test_utils.interfaces import UpdatedDummySensorInterface

    dummy_sensor.interface = fqn(UpdatedDummySensorInterface)
    dummy_sensor.visible = True
    dummy_sensor.status = {"dummy_key": "dummy_value"}
    dummy_sensor.last_status_update = datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    dummy_sensor.last_update_status = dummy_sensor.UpdateStatus.SUCCESS
    dummy_sensor.last_status_update_log = "Dummy Sensor OK"
    dummy_sensor.save()
    return dummy_sensor


@pytest.mark.selenium
def test_home_page_sensor_auto_update_disabled(selenium: "WebDriver", live_server: "LiveServer",
                                               dummy_sensor_ui: "Sensor", templates_for_testing: "SettingsWrapper") -> None:
    selenium.get(f"{live_server.url}/invalid_url_used_for_cookie_creation/")
    selenium.add_cookie({"name": "auto_update_flag", "value": "false", "path": "/"})

    selenium.get(live_server.url)

    dummy_sensor_card = selenium.find_element(By.ID, dummy_sensor_ui.slug)
    status_dummy_key = dummy_sensor_card.find_element(By.ID, f"{ dummy_sensor_ui.slug }-status-dummy_key")
    assert status_dummy_key.text == dummy_sensor_ui.status["dummy_key"]
    last_status_update = dummy_sensor_card.find_element(By.ID, f"{ dummy_sensor_ui.slug }-last_status_update")
    assert last_status_update.text == dummy_sensor_ui.last_status_update.strftime("%Y-%m-%d %H:%M:%S")
    last_update_status = dummy_sensor_card.find_element(By.ID, f"{ dummy_sensor_ui.slug }-last_update_status")
    assert last_update_status.text == dummy_sensor_ui.get_last_update_status_display()
    assert last_update_status.get_attribute("title") == dummy_sensor_ui.last_status_update_log


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_sensor_with_auto_update(selenium: "WebDriver", live_server: "LiveServer",
                                           dummy_sensor_ui: "Sensor", templates_for_testing: "SettingsWrapper") -> None:
    selenium.get(live_server.url)

    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_sensor_ui.slug }-status-dummy_key"),
            "updated_dummy_value")
    )
    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_sensor_ui.slug }-last_status_update"),
            localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    last_update_status = selenium.find_element(By.ID, f"{dummy_sensor_ui.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-check-circle')
    )
    assert last_update_status.get_attribute("title") == "Sensor status updated successfully"


@pytest.mark.selenium
def test_home_page_sensor_refresh_button(selenium: "WebDriver", live_server: "LiveServer",
                                           dummy_sensor_ui: "Sensor", templates_for_testing: "SettingsWrapper") -> None:
    selenium.get(live_server.url)

    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_sensor_ui.slug }-status-dummy_key"),
            "updated_dummy_value")
    )

    refresh_button = selenium.find_element(By.ID, f"{dummy_sensor_ui.slug}-refresh")
    refresh_button.click()

    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_sensor_ui.slug }-status-dummy_key"),
            "updated_dummy_value_another_time")
    )
