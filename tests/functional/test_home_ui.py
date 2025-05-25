import pytest
import typing
from unittest.mock import Mock
from strategy_field.utils import fqn
from freezegun import freeze_time
from datetime import datetime
from django.utils.timezone import localtime, now
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

if typing.TYPE_CHECKING:
    from rpi_controller.models import Device, Sensor, Actuator, Controller
    from rpi_controller.interfaces import Interface
    from pytest_django.fixtures import SettingsWrapper
    from selenium.webdriver.remote.webdriver import WebDriver
    from pytest_django.live_server_helper import LiveServer
    from _pytest.fixtures import TopRequest


def __configure_device_on_ui(dummy_device: "Device", device_interface: type["Interface"]) -> "Device":
    dummy_device.interface = fqn(device_interface)
    dummy_device.visible = True
    dummy_device.status = {"dummy_key": "dummy_value"}
    dummy_device.last_status_update_time = datetime.strptime("1900-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    dummy_device.last_update_status = dummy_device.UpdateStatus.SUCCESS
    dummy_device.last_status_update_log = f"Dummy {dummy_device.__class__.__name__} OK"
    dummy_device.save()
    return typing.cast("Device", dummy_device)


def __configure_device_for_error_on_ui(dummy_device: "Device", device_interface: type["Interface"]) -> "Device":
    dummy_device.interface = fqn(device_interface)
    dummy_device.save()
    return dummy_device


@pytest.fixture
def dummy_sensor_ui(dummy_sensor: "Sensor") -> "Sensor":
    from test_utils.interfaces import UpdatedDummySensorInterface
    UpdatedDummySensorInterface.read_input_mock = Mock(
        side_effect=[
            {"dummy_key": "updated_dummy_value"},
            {"dummy_key": "updated_dummy_value_another_time"}
        ]
    )
    return typing.cast("Sensor", __configure_device_on_ui(dummy_sensor, UpdatedDummySensorInterface))


@pytest.fixture
def dummy_sensor_ui_error(dummy_sensor_ui: "Sensor") -> "Sensor":
    from test_utils.interfaces import DummyErrorSensorInterface
    return typing.cast("Sensor", __configure_device_for_error_on_ui(dummy_sensor_ui, DummyErrorSensorInterface))



@pytest.fixture
def dummy_actuator_ui(dummy_actuator: "Actuator") -> "Actuator":
    from test_utils.interfaces import UpdatedDummyActuatorInterface
    return typing.cast("Actuator", __configure_device_on_ui(dummy_actuator, UpdatedDummyActuatorInterface))


@pytest.fixture
def dummy_actuator_ui_error(dummy_actuator_ui: "Actuator") -> "Actuator":
    from test_utils.interfaces import DummyActuatorErrorInterface
    return typing.cast("Actuator", __configure_device_for_error_on_ui(dummy_actuator_ui, DummyActuatorErrorInterface))


@pytest.fixture
def dummy_controller_ui(dummy_controller: "Controller") -> "Controller":
    from test_utils.interfaces import UpdatedDummyControllerInterface

    controller: "Controller" = typing.cast(
        "Controller", __configure_device_on_ui(dummy_controller, UpdatedDummyControllerInterface)
    )
    controller.status["flag"] = False
    controller.save()

    return controller


@pytest.fixture
def dummy_controller_ui_error(dummy_controller_ui: "Controller") -> "Controller":
    from test_utils.interfaces import DummyControllerErrorInterface
    return typing.cast("Controller", __configure_device_for_error_on_ui(dummy_controller_ui, DummyControllerErrorInterface))


@pytest.mark.selenium
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_sensor_ui", id="sensor"),
    pytest.param("dummy_actuator_ui", id="actuator"),
    pytest.param("dummy_controller_ui", id="controller"),
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
    assert last_update_status.get_attribute("title") == "(Interface Error): Sensor error"


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
@pytest.mark.selenium
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_actuator_ui", id="actuator"),
    pytest.param("dummy_controller_ui", id="controller"),
])
def test_home_page_non_sensor_with_auto_update(selenium: "WebDriver", live_server: "LiveServer",
                                               device_fixture_name: str, request: "TopRequest",
                                               templates_for_testing: "SettingsWrapper") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    selenium.get(live_server.url)

    dummy_device_card = selenium.find_element(By.ID, dummy_device.slug)
    status_dummy_key = dummy_device_card.find_element(By.ID, f"{ dummy_device.slug }-status-dummy_key")
    assert status_dummy_key.text == dummy_device.status["dummy_key"]
    last_status_update_time = dummy_device_card.find_element(By.ID, f"{ dummy_device.slug }-last_status_update_time")
    assert last_status_update_time.text == dummy_device.last_status_update_time.strftime("%Y-%m-%d %H:%M:%S")

    last_update_status = selenium.find_element(By.ID, f"{dummy_device.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-check-circle')
    )
    assert last_update_status.get_attribute("title") == dummy_device.last_status_update_log


@pytest.mark.selenium
@pytest.mark.parametrize("device_fixture_name", [
    pytest.param("dummy_actuator_ui", id="actuator"),
    pytest.param("dummy_controller_ui", id="controller"),
])
def test_home_page_non_sensor_refresh_button(selenium: "WebDriver", live_server: "LiveServer",
                                             device_fixture_name: str, request: "TopRequest",
                                             templates_for_testing: "SettingsWrapper") -> None:
    dummy_device: "Device" = request.getfixturevalue(device_fixture_name)

    selenium.get(f"{live_server.url}/invalid_url_used_for_cookie_creation/")
    selenium.add_cookie({"name": "auto_update_flag", "value": "false", "path": "/"})

    selenium.get(live_server.url)

    dummy_device_card = selenium.find_element(By.ID, dummy_device.slug)
    last_update_status = dummy_device_card.find_element(By.ID, f"{dummy_device.slug}-last_update_status")
    assert last_update_status.text == dummy_device.get_last_update_status_display()

    refresh_button = selenium.find_element(By.ID, f"{dummy_device.slug}-refresh")
    refresh_button.click()

    last_update_status = selenium.find_element(By.ID, f"{dummy_device.slug}-last_update_status")
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
    assert last_update_status.get_attribute("title") == "(Interface Error): Actuator error"

    dummy_actuator_ui_error.refresh_from_db()
    assert not dummy_actuator_ui_error.status.get("flag", None)


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_controller_control_status(selenium: "WebDriver", live_server: "LiveServer",
                                             dummy_controller_ui: "Controller",
                                             templates_for_testing: "SettingsWrapper") -> None:
    assert not dummy_controller_ui.status.get("flag", None)  # Sanity check

    selenium.get(live_server.url)

    dummy_controller_card = selenium.find_element(By.ID, dummy_controller_ui.slug)
    status_flag = dummy_controller_card.find_element(By.ID, f"{ dummy_controller_ui.slug }-status-flag")
    assert WebDriverWait(selenium, 5).until(
        lambda d: status_flag.text == "false"
    )

    control_button = dummy_controller_card.find_element(By.ID, f"{dummy_controller_ui.slug}-control")
    control_button.click()

    assert WebDriverWait(selenium, 5).until(
        lambda d: status_flag.text == "true"
    )
    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_controller_ui.slug }-last_status_update_time"),
            localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    last_update_status = selenium.find_element(By.ID, f"{dummy_controller_ui.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-check-circle')
    )
    assert last_update_status.get_attribute("title") == "Controller status updated successfully"

    dummy_controller_ui.refresh_from_db()
    assert dummy_controller_ui.status["flag"]


@pytest.mark.selenium
@freeze_time("2000-01-01 00:00:00")
def test_home_page_controller_control_status_error(selenium: "WebDriver", live_server: "LiveServer",
                                                   dummy_controller_ui_error: "Controller",
                                                   templates_for_testing: "SettingsWrapper") -> None:
    assert not dummy_controller_ui_error.status.get("flag", None)  # Sanity check

    selenium.get(live_server.url)

    dummy_controller_card = selenium.find_element(By.ID, dummy_controller_ui_error.slug)
    status_flag = dummy_controller_card.find_element(By.ID, f"{ dummy_controller_ui_error.slug }-status-flag")
    assert WebDriverWait(selenium, 5).until(
        lambda d: status_flag.text == "false"
    )

    control_button = dummy_controller_card.find_element(By.ID, f"{dummy_controller_ui_error.slug}-control")
    control_button.click()

    assert WebDriverWait(selenium, 5).until(
        lambda d: status_flag.text == "false"
    )
    assert WebDriverWait(selenium, 5).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, f"{ dummy_controller_ui_error.slug }-last_status_update_time"),
            localtime(now()).strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    last_update_status = selenium.find_element(By.ID, f"{dummy_controller_ui_error.slug}-last_update_status")
    assert WebDriverWait(selenium, 5).until(
        lambda d: last_update_status.find_element(By.CLASS_NAME, 'bi-exclamation-circle')
    )
    assert last_update_status.get_attribute("title") == "(Interface Error): Controller error"

    dummy_controller_ui_error.refresh_from_db()
    assert not dummy_controller_ui_error.status["flag"]
