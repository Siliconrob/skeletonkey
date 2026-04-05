import copy
from dataclasses import dataclass

from RecordTypes.Step import StepStatus, Step, StepArgs


@dataclass
class WriteFile(Step):
    def perform_step(self, *args, **kwargs) -> StepArgs:
        action_name = f"{self.__class__.__name__}:{self.perform_step.__name__}"

        destination_path = kwargs.get("destination_path", None)
        if destination_path is None:
            raise Exception(f"{action_name} {self.id=} {args=} {kwargs=}  failed")
        print(f"{action_name} {self.id=} completed")
        return StepArgs(
            run=copy.deepcopy(kwargs), undo=dict(perform_step=StepStatus.SUCCESS)
        )

    def undo_step(self, *args, **kwargs) -> None:
        action_name = f"{self.__class__.__name__}:{self.undo_step.__name__}"
        if kwargs.get("fail", False):
            raise Exception(f"{action_name} {self.id=} {args=} {kwargs=} failed")
        print(f"{action_name} {self.id=} completed")


@dataclass
class DoSomething(Step):
    def perform_step(self, *args, **kwargs) -> StepArgs:
        action_name = f"{self.__class__.__name__}:{self.perform_step.__name__}"
        if kwargs.get("fail", False):
            raise Exception(f"{action_name} {self.id=} {args=} {kwargs=}  failed")
        print(f"{action_name} {self.id=} completed")
        return StepArgs(
            run=copy.deepcopy(kwargs), undo=dict(perform_step=StepStatus.SUCCESS)
        )

    def undo_step(self, *args, **kwargs) -> None:
        action_name = f"{self.__class__.__name__}:{self.undo_step.__name__}"
        if kwargs.get("fail", False):
            raise Exception(f"{action_name} {self.id=} {args=} {kwargs=} failed")
        print(f"{action_name} {self.id=} completed")
