from abc import abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, Literal
from datetime import datetime, timezone


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
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] = field(default_factory=dict)

@dataclass
class Step(Protocol):

    def __post_init__(self):
        self._status.append(StatusEntry(identifier=StepStatus.PENDING,
                                        method=self.run.__name__,
                                        timestamp=datetime.now(tz=timezone.utc)))
    id: int = 0
    _status: list[StatusEntry] = field(default_factory=list)
    previous_step: Step | None = None
    next_step: Step | None = None

    @property
    def current_status(self) -> StatusEntry:
        return self._status[-1]

    @property
    def status_history(self) -> str:
        results:list[str] = []
        for entry in sorted(self._status, key=lambda x: x.timestamp.timestamp()):
            results.append(f'{entry.timestamp.isoformat()}: {entry.method}, {entry.identifier.value}')
        return '\n'.join(results)

    @abstractmethod
    def run(self,  *args, **kwargs) -> Step | None:
        ...

    @abstractmethod
    def rollback(self,  *args, **kwargs) -> Step | None:
        ...

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


@dataclass
class DoSomething(Step):
    def rollback(self,  *args, **kwargs) -> Step | None:
        action_name = self.rollback.__name__
        if kwargs.get("fail", False):
            self._status.append(StatusEntry(identifier=StepStatus.FAILURE,
                                            method=action_name,
                                            args=args,
                                            kwargs=kwargs,
                                            timestamp=datetime.now(tz=timezone.utc)))

            raise Exception(f'{action_name} {self.id=} {args=} {kwargs=}  failed')
        self._status.append(StatusEntry(identifier=StepStatus.SUCCESS,
                                        method=action_name,
                                        args=args,
                                        kwargs=kwargs,
                                        timestamp=datetime.now(tz=timezone.utc)))
        print(self.status_history)
        print(f'{action_name} {self.id=} completed')
        return self.previous()

    def run(self, *args, **kwargs) -> Step | None:
        action_name = self.run.__name__

        if kwargs.get("fail", False):
            self._status.append(StatusEntry(identifier=StepStatus.FAILURE,
                                            method=action_name,
                                            args=args,
                                            kwargs=kwargs,
                                            timestamp=datetime.now(tz=timezone.utc)))
            raise Exception(f'{action_name} {self.id=} {args=} {kwargs=} failed')
        self._status.append(StatusEntry(identifier=StepStatus.SUCCESS,
                                        method=action_name,
                                        args=args,
                                        kwargs=kwargs,
                                        timestamp=datetime.now(tz=timezone.utc)))
        print(self.status_history)
        print(f'{action_name} {self.id=} completed')
        return self.next()