import typing
from functools import wraps
from django.db import transaction

if typing.TYPE_CHECKING:
    from rpi_controller.interfaces import Interface


def lock_db_record(func: typing.Callable[..., typing.Any]) -> typing.Callable[..., typing.Any]:
    @wraps(func)
    def wrapper(self: "Interface", *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        with transaction.atomic():
            # Lock model object to avoid concurrent read on the same device
            type(self.context).objects.select_for_update().get(id=self.context.id)
            return func(self, *args, **kwargs)
    return wrapper
