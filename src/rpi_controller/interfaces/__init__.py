import typing
from abc import ABC

from strategy_field.registry import Registry


class InterfaceRegistry(Registry):
    def __init__(self, base_class: typing.Any, *args: typing.Any, **kwargs: typing.Any) -> None:
        kwargs.setdefault("label_attribute", "label")
        super().__init__(base_class, *args, **kwargs)


class Interface(ABC):
    label: str
    config_class = None

    def __init__(self, context: typing.Any) -> None:
        self.context = context
