import typing
import pytest

if typing.TYPE_CHECKING:
    from rpi_controller.models import Sensor


@pytest.fixture
def dummy_sensor() -> Sensor:
    from test_utils.factories import SensorFactory
    return SensorFactory.create()
