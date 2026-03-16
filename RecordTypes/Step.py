from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol, Callable


class StepStatus(Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    ROLLBACK = "rollback"


@dataclass(frozen=True)
class StatusEntry:
    identifier: StepStatus
    timestamp: datetime
    method: str = "unknown"

@dataclass
class StepArgs:
    run: dict[str, Any] = field(default_factory=dict)
    undo: dict[str, Any] = field(default_factory=dict)


@dataclass
class Step(ABC):

    # def __post_init__(self):
    #     self._status.append(StatusEntry(identifier=StepStatus.PENDING,
    #                                     method=self.run.__name__,
    #                                     timestamp=datetime.now(tz=timezone.utc)))
    id: int = 0
    previous_step: Step | None = None
    next_step: Step | None = None
    args: StepArgs = field(default_factory=StepArgs)

    # @property
    # def current_status(self) -> StatusEntry:
    #     return self._status[-1]

    # @property
    # def status_history(self) -> str:
    #     results:list[str] = []
    #     for entry in sorted(self._status, key=lambda x: x.timestamp.timestamp()):
    #         results.append(f'{entry.timestamp.isoformat()}: {entry.method}, {entry.identifier.value}')
    #     return '\n'.join(results)

    @abstractmethod
    def perform_step(self, *args, **kwargs) -> StepArgs:
        ...

    @abstractmethod
    def undo_step(self,  *args, **kwargs) -> None:
        ...

    def run(self, *args, **kwargs) -> Step | None:
        output = self.perform_step(*args, **kwargs)
        self.args.undo= output.undo
        next_step = self.next()
        if next_step is None:
            return next_step
        next_step.args.run.update(output.run)
        return next_step

    def rollback(self) -> Step | None:
        self.undo_step(**self.args.undo)
        return self.previous()

    def next(self) -> Step | None:
        if self.next_step is None:
            return None
        return self.next_step

    def previous(self) -> Step | None:
        if self.previous_step is None:
            return None
        return self.previous_step


def build_steps(steps: list[Step]) -> Step:
    start = steps[0]
    for i, step in enumerate(steps):
        step.id = i + 1
        if i == 0:
            step.previous_step = None
        else:
            step.previous_step = steps[i-1]
        step.next_step = steps[i + 1] if i < len(steps) - 1 else None
    return start