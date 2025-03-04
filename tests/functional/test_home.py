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
    from rpi_controller.models import Sensor, Actuator, Device
    from pytest_django.fixtures import SettingsWrapper
    from selenium.webdriver.remote.webdriver import WebDriver
    from pytest_django.live_server_helper import LiveServer
    from _pytest.fixtures import TopRequest


@pytest.fixture
def dummy_sensor_ui(dummy_sensor: "Sensor") -> "Sensor":
    from test_utils.interfaces import UpdatedDummySensorInterface

    dummy_sensor.interface = fqn(UpdatedDummySensorInterface)
    dummy_sensor.visible = True
    dummy_sensor.status = {"dummy_key": "dummy_value"}
    dummy_sensor.last_status_update_time = datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    dummy_sensor.last_update_status = dummy_sensor.UpdateStatus.SUCCESS
    dummy_sensor.last_status_update_log = "Dummy Sensor OK"
    dummy_sensor.save()
    return dummy_sensor


@pytest.fixture
def dummy_sensor_ui_error(dummy_sensor_ui: "Sensor") -> "Sensor":
    from test_utils.interfaces import DummyErrorSensorInterface

    dummy_sensor_ui.interface = fqn(DummyErrorSensorInterface)
    dummy_sensor_ui.save()
    return dummy_sensor_ui



@pytest.fixture
def dummy_actuator_ui(dummy_actuator: "Actuator") -> "Actuator":
    from test_utils.interfaces import UpdatedDummyActuatorInterface

    dummy_actuator.interface = fqn(UpdatedDummyActuatorInterface)
    dummy_actuator.visible = True
    dummy_actuator.status = {"dummy_key": "dummy_value"}
    dummy_actuator.last_status_update_time = datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    dummy_actuator.last_update_status = dummy_actuator.UpdateStatus.SUCCESS
    dummy_actuator.last_status_update_log = "Dummy Actuator OK"
    dummy_actuator.save()
    return dummy_actuator


@pytest.fixture
def dummy_actuator_ui_error(dummy_actuator_ui: "Actuator") -> "Actuator":
    from test_utils.interfaces import DummyActuatorErrorInterface

    dummy_actuator_ui.interface = fqn(DummyActuatorErrorInterface)
    dummy_actuator_ui.status = {}
    dummy_actuator_ui.save()
    return dummy_actuator_ui



@pytest.mark.selenium
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor_ui", id="sensor"),
    pytest.param("dummy_actuator_ui", id="actuator"),
])
def test_home_page_device_auto_update_disabled(selenium: "WebDriver", live_server: "LiveServer",
                                               device_fixture_name: str, request: "TopRequest",
                                               templates_for_testing: "SettingsWrapper") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    selenium.get(f"{live_server.url}/invalid_url_used_for_cookie_creation/")
    selenium.add_cookie({"name": "auto_update_flag", "value": "false", "path": "/"})

    selenium.get(live_server.url)

    dummy_device_card = selenium.find_element(By.ID, dummy_device.slug)
    status_dummy_key = dummy_device_card.find_element(By.ID, f"{ dummy_device.slug }-status-dummy_key")
    assert status_dummy_key.text == dummy_device.status["dummy_key"]
    last_status_update_time = dummy_device_card.find_element(By.ID, f"{ dummy_device.slug }-last_status_update_time")
    assert last_status_update_time.text == dummy_device.last_status_update_time.strftime("%Y-%m-%d %H:%M:%S")
    last_update_status = dummy_device_card.find_element(By.ID, f"{ dummy_device.slug }-last_update_status")
    assert last_update_status.text == dummy_device.get_last_update_status_display()
    assert last_update_status.get_attribute("title") == dummy_device.last_status_update_log


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
            (By.ID, f"{ dummy_sensor_ui.slug }-last_status_update_time"),
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


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_sensor_update_error(selenium: "WebDriver", live_server: "LiveServer",
                                       dummy_sensor_ui_error: "Sensor",
                                       templates_for_testing: "SettingsWrapper") -> None:
    selenium.get(f"{live_server.url}/invalid_url_used_for_cookie_creation/")
    selenium.add_cookie({"name": "auto_update_flag", "value": "false", "path": "/"})

    selenium.get(live_server.url)

    dummy_device_card = selenium.find_element(By.ID, dummy_sensor_ui_error.slug)
    last_status_update_time = dummy_device_card.find_element(By.ID, f"{ dummy_sensor_ui_error.slug }-last_status_update_time")
    assert last_status_update_time.text == dummy_sensor_ui_error.last_status_update_time.strftime("%Y-%m-%d %H:%M:%S")
    last_update_status = dummy_device_card.find_element(By.ID, f"{ dummy_sensor_ui_error.slug }-last_update_status")
    assert last_update_status.text == dummy_sensor_ui_error.get_last_update_status_display()
    assert last_update_status.get_attribute("title") == dummy_sensor_ui_error.last_status_update_log

    refresh_button = selenium.find_element(By.ID, f"{dummy_sensor_ui_error.slug}-refresh")
    refresh_button.click()

    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_sensor_ui_error.slug }-last_status_update_time"),
            localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    last_update_status = selenium.find_element(By.ID, f"{dummy_sensor_ui_error.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-exclamation-circle')
    )
    assert last_update_status.get_attribute("title") == "Sensor error"




@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_actuator_with_auto_update(selenium: "WebDriver", live_server: "LiveServer",
                                             dummy_actuator_ui: "Actuator",
                                             templates_for_testing: "SettingsWrapper") -> None:
    selenium.get(live_server.url)

    dummy_actuator_card = selenium.find_element(By.ID, dummy_actuator_ui.slug)
    status_dummy_key = dummy_actuator_card.find_element(By.ID, f"{ dummy_actuator_ui.slug }-status-dummy_key")
    assert status_dummy_key.text == dummy_actuator_ui.status["dummy_key"]
    last_status_update_time = dummy_actuator_card.find_element(By.ID, f"{ dummy_actuator_ui.slug }-last_status_update_time")
    assert last_status_update_time.text == dummy_actuator_ui.last_status_update_time.strftime("%Y-%m-%d %H:%M:%S")

    last_update_status = selenium.find_element(By.ID, f"{dummy_actuator_ui.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-check-circle')
    )
    assert last_update_status.get_attribute("title") == dummy_actuator_ui.last_status_update_log


@pytest.mark.selenium
def test_home_page_actuator_refresh_button(selenium: "WebDriver", live_server: "LiveServer",
                                           dummy_actuator_ui: "Actuator",
                                           templates_for_testing: "SettingsWrapper") -> None:
    selenium.get(f"{live_server.url}/invalid_url_used_for_cookie_creation/")
    selenium.add_cookie({"name": "auto_update_flag", "value": "false", "path": "/"})

    selenium.get(live_server.url)

    dummy_actuator_card = selenium.find_element(By.ID, dummy_actuator_ui.slug)
    last_update_status = dummy_actuator_card.find_element(By.ID, f"{dummy_actuator_ui.slug}-last_update_status")
    assert last_update_status.text == dummy_actuator_ui.get_last_update_status_display()

    refresh_button = selenium.find_element(By.ID, f"{dummy_actuator_ui.slug}-refresh")
    refresh_button.click()

    last_update_status = selenium.find_element(By.ID, f"{dummy_actuator_ui.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-check-circle')
    )


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_actuator_change_status(selenium: "WebDriver", live_server: "LiveServer",
                                          dummy_actuator_ui: "Actuator",
                                          templates_for_testing: "SettingsWrapper") -> None:

    assert not dummy_actuator_ui.status.get("flag", None)  # Sanity check

    selenium.get(live_server.url)

    dummy_actuator_card = selenium.find_element(By.ID, dummy_actuator_ui.slug)
    status_flag = dummy_actuator_card.find_element(By.ID, f"{ dummy_actuator_ui.slug }-status-flag")
    assert not status_flag.get_attribute("checked")

    status_flag.click()

    assert WebDriverWait(selenium, 5).until(
        lambda d: status_flag.get_attribute("checked")
    )
    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_actuator_ui.slug }-last_status_update_time"),
            localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    last_update_status = selenium.find_element(By.ID, f"{dummy_actuator_ui.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-check-circle')
    )
    assert last_update_status.get_attribute("title") == "Actuator status updated successfully"

    dummy_actuator_ui.refresh_from_db()
    assert dummy_actuator_ui.status["flag"]


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_actuator_change_status_error(selenium: "WebDriver", live_server: "LiveServer",
                                                dummy_actuator_ui_error: "Actuator",
                                                templates_for_testing: "SettingsWrapper") -> None:

    assert not dummy_actuator_ui_error.status.get("flag", None)  # Sanity check

    selenium.get(live_server.url)

    dummy_actuator_card = selenium.find_element(By.ID, dummy_actuator_ui_error.slug)
    status_flag = dummy_actuator_card.find_element(By.ID, f"{ dummy_actuator_ui_error.slug }-status-flag")
    assert not status_flag.get_attribute("checked")

    status_flag.click()

    assert WebDriverWait(selenium, 5).until(
        lambda d: not status_flag.get_attribute("checked")
    )
    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_actuator_ui_error.slug }-last_status_update_time"),
            localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    last_update_status = selenium.find_element(By.ID, f"{dummy_actuator_ui_error.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-exclamation-circle')
    )
    assert last_update_status.get_attribute("title") == "Actuator error"

    dummy_actuator_ui_error.refresh_from_db()
    assert not dummy_actuator_ui_error.status.get("flag", None)
