import uuid
from abc import abstractmethod
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol


class StepStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"

@dataclass
class Step(Protocol):
    name: str = f'step_name_{uuid.uuid4().hex}'
    _status: StepStatus = StepStatus.PENDING
    previous_step: Step | None = None
    next_step: Step | None = None
    # _temporary_data: dict[str, Any] = field(default_factory=dict)

    @property
    def current_status(self) -> StepStatus:
        return self._status

    @abstractmethod
    def process(self,  *args, **kwargs) -> Step | None:
        ...

    @abstractmethod
    def undo(self,  *args, **kwargs) -> Step | None:
        ...

    # def create_temporary_data(self, *args, **kwargs) -> None:
    #     self._temporary_data = kwargs

    # def cleanup(self) -> None:
    #     current_step = self
    #     while current_step.next_step is not None:
    #         del self._temporary_data
    #         current_step = current_step.next()  # type: ignore[assignment]

    def next(self) -> Step | None:
        if self.next_step is None:
            return None
        return self.next_step

    def previous(self) -> Step | None:
        if self.previous_step is None:
            return None
        return self.previous_step


def construct_steps(steps: list[Step]) -> Step:
    start = steps[0]
    for i, step in enumerate(steps):
        if i == 0:
            step.previous_step = None
        else:
            step.previous_step = steps[i-1]
        step.next_step = steps[i + 1] if i < len(steps) - 1 else None
    return start


@dataclass
class DoSomething(Step):
    def undo(self, *args, **kwargs) -> Step | None:
        if kwargs.get("fail", False):
            self._status = StepStatus.FAILURE
            raise Exception("Not implemented")
        self._status = StepStatus.SUCCESS
        print("Undo completed")
        return self.previous()

    def process(self, *args, **kwargs) -> Step | None:
        if kwargs.get("fail", False):
            self._status = StepStatus.FAILURE
            raise Exception("Not implemented")
        self._status = StepStatus.SUCCESS
        print("Process completed")
        return self.next()