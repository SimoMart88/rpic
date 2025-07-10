import os
import typing
import pytest
from pathlib import Path
from importlib import reload


if typing.TYPE_CHECKING:
    import types
    from django.contrib.auth.models import User
    from rpi_controller.models import Sensor, Actuator, Controller
    from pytest_django.fixtures import SettingsWrapper
    from pytest import Parser, Config
    from django_celery_beat.models import PeriodicTask


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

    # Force disable Sentry by setting environment variable
    os.environ["SENTRY_DSN"] = ""


@pytest.fixture(autouse=True)
def common_tests_settings(settings: "SettingsWrapper") -> None:
    settings.TIME_ZONE = "Etc/UTC"


@pytest.fixture(autouse=True)
def system_monitor_mock(settings: "SettingsWrapper") -> "types.ModuleType":
    from rpi_controller import monitoring

    settings.SYSTEM_MONITORS = {
        "default": {
            "BACKEND": "test_utils.monitoring.DummySystemMonitor",
            "LOCATION": "dummy"
        }
    }
    reload(monitoring)

    return monitoring


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
def staff_user() -> "User":
    from test_utils.factories import StaffUserFactory
    return StaffUserFactory.create()


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
def dummy_periodic_task() -> "PeriodicTask":
    from django_celery_beat.models import PeriodicTask, CrontabSchedule
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
