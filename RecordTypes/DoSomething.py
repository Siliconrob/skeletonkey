import copy
from dataclasses import dataclass
from datetime import datetime, timezone

from RecordTypes.Step import StatusEntry, StepStatus, Step, StepArgs


@dataclass
class DoSomething(Step):
    def perform_step(self,  *args, **kwargs) -> StepArgs:
        action_name = self.rollback.__name__
        if kwargs.get("fail", False):
            self._status.append(StatusEntry(identifier=StepStatus.FAILURE,
                                            method=action_name,
                                            timestamp=datetime.now(tz=timezone.utc)))

            raise Exception(f'{action_name} {self.id=} {args=} {kwargs=}  failed')
        self._status.append(StatusEntry(identifier=StepStatus.SUCCESS,
                                        method=action_name,
                                        timestamp=datetime.now(tz=timezone.utc)))
        print(self.status_history)
        print(f'{action_name} {self.id=} completed')
        return StepArgs(run=copy.deepcopy(kwargs), undo=dict(perform_step=StepStatus.SUCCESS))

    def undo_step(self, *args, **kwargs) -> None:
        action_name = self.run.__name__
        if kwargs.get("fail", False):
            self._status.append(StatusEntry(identifier=StepStatus.FAILURE,
                                            method=action_name,
                                            timestamp=datetime.now(tz=timezone.utc)))
            raise Exception(f'{action_name} {self.id=} {args=} {kwargs=} failed')
        self._status.append(StatusEntry(identifier=StepStatus.SUCCESS,
                                        method=action_name,
                                        timestamp=datetime.now(tz=timezone.utc)))
        print(self.status_history)
        print(f'{action_name} {self.id=} completed')