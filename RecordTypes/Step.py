from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class Step(Protocol):
    name: str

    @abstractmethod
    def process(self, inputs: Any) -> Any:
        ...

    @abstractmethod
    def undo(self, inputs: Any) -> Any:
        ...

    @abstractmethod
    def delete_ephemeral_data(self) -> Any:
        ...

    def next(self) -> Step | None:
        if self._next_step is None:
            return None
        return self._next_step

    def previous(self) -> Step | None:
        self.delete_ephemeral_data()
        if self._previous_step is None:
            return None
        return self._previous_step

    _previous_step: Step | None
    _next_step: Step | None


