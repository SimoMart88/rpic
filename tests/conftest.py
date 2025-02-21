import typing
import pytest
from pathlib import Path


if typing.TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rpi_controller.models import Sensor, Actuator
    from pytest_django.fixtures import SettingsWrapper
    from pytest import Parser, Config


BASE_DIR = Path(__file__).resolve().parent


def pytest_addoption(parser: "Parser") -> None:
    parser.addoption(
        '--no-selenium',
        action='store_true',
        dest='disable_selenium',
        default=False,
        help='Enable Selenium tests',
    )
    parser.addoption(
        '--show-browser',
        '-S',
        action='store_true',
        dest='show_browser',
        default=False,
        help='will display start browsers in selenium tests',
    )


def pytest_configure(config: "Config") -> None:
    if config.option.disable_selenium:
        setattr(config.option, 'markexpr', 'not selenium')

    if not config.option.driver:
        setattr(config.option, 'driver', 'chrome')

    if not config.option.driver_path:
        from webdriver_manager.chrome import ChromeDriverManager
        setattr(config.option, 'driver_path', ChromeDriverManager().install())


@pytest.fixture()
def templates_for_testing(settings: "SettingsWrapper") -> "SettingsWrapper":
    new_templates_config = settings.TEMPLATES
    new_templates_config[0]["DIRS"].append(BASE_DIR / "test_utils" / "templates")
    settings.TEMPLATES = new_templates_config
    return settings


@pytest.fixture
def dummy_sensor() -> "Sensor":
    from test_utils.factories import SensorFactory
    return SensorFactory.create()


@pytest.fixture
def dummy_actuator() -> "Actuator":
    from test_utils.factories import ActuatorFactory
    return ActuatorFactory.create()


@pytest.fixture
def admin_user() -> "User":
    from test_utils.factories import SuperUserFactory
    return SuperUserFactory.create()
