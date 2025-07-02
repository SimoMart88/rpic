import typing
import rpi_controller


if typing.TYPE_CHECKING:
    from django.http import HttpRequest


def app_info(request: "HttpRequest") -> dict[str, dict[str, str]]:
    return {
        "rpic": {
            "version": rpi_controller.__version__,
        }
    }
