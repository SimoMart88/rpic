from typing import Any
from abc import ABC


class Interface(ABC):
    config_class = None

    def __init__(self, context: Any) -> None:
        self.context = context
