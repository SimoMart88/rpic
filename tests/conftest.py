import typing
import pytest
from pathlib import Path

from django_celery_beat.models import PeriodicTask, CrontabSchedule


if typing.TYPE_CHECKING:
    from django.contrib.auth.models import User
    from rpi_controller.models import Sensor, Actuator, Controller
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


@pytest.fixture(autouse=True)
def common_tests_settings(settings: "SettingsWrapper") -> None:
    settings.TIME_ZONE = "Etc/UTC"
    settings.CELERY_RESULT_BACKEND = "memory:///"


@pytest.fixture()
def templates_for_testing(settings: "SettingsWrapper") -> "SettingsWrapper":
    new_templates_config = settings.TEMPLATES
    new_templates_config[0]["DIRS"].append(BASE_DIR / "test_utils" / "templates")
    settings.TEMPLATES = new_templates_config
    return settings


@pytest.fixture
def admin_user() -> "User":
    from test_utils.factories import SuperUserFactory
    return SuperUserFactory.create()


@pytest.fixture
def dummy_sensor() -> "Sensor":
    from test_utils.factories import SensorFactory
    return SensorFactory.create()


@pytest.fixture
def dummy_actuator() -> "Actuator":
    from test_utils.factories import ActuatorFactory
    return ActuatorFactory.create()


@pytest.fixture
def dummy_controller() -> "Controller":
    from test_utils.factories import ControllerFactory
    return ControllerFactory.create()


@pytest.fixture
def dummy_periodic_task() -> PeriodicTask:
    crontab, _ = CrontabSchedule.objects.get_or_create(
        minute="*/5", hour="*", day_of_week="*",
        month_of_year="*", day_of_month="*",
        timezone="Etc/UTC",
    )
    periodic_task = PeriodicTask.objects.create(
        name="Trigger every 5 minutes",
        enabled=True,
        task="dummy_task",
        crontab=crontab
    )
    return periodic_task
