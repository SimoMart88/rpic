import typing
from functools import wraps
from django.core.cache import cache


if typing.TYPE_CHECKING:
    from rpi_controller.interfaces import Interface


def lock_device(func: typing.Callable[..., typing.Any]) -> typing.Callable[..., typing.Any]:
    @wraps(func)
    def wrapper(self: "Interface", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        ModelClass = type(self.context)
        lock_timeout = self.context.config.get("lock_timeout", 60*5)
        with cache.lock(f"{ModelClass.__name__}-{self.context.id}", timeout=lock_timeout):
            # Lock model object to avoid concurrent operation on the same device
            return func(self, *args, **kwargs)

    return wrapper
