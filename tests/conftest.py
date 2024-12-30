import typing
import pytest
from pathlib import Path


if typing.TYPE_CHECKING:
    from pytest_django.fixtures import SettingsWrapper


BASE_DIR = Path(__file__).resolve().parent


@pytest.fixture()
def templates_for_testing(settings: "SettingsWrapper") -> "SettingsWrapper":
    new_templates_config = settings.TEMPLATES
    new_templates_config[0]["DIRS"].append(BASE_DIR / "test_utils" / "templates")
    settings.TEMPLATES = new_templates_config
    return settings
