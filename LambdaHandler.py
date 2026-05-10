import dataclasses
import json
from typing import Any

from camel_converter import dict_to_snake


@dataclasses.dataclass(frozen=True, kw_only=True)
class CommandEventArgs:
    show_all: bool = False
    user_id: str | None = None



@dataclasses.dataclass(frozen=True, kw_only=True)
class CommandEvent:
    cmd: str
    sub_command: str | None
    args: CommandEventArgs | None = None


def run_fn(event: dict[str, Any], context: dict[str, Any]) -> Any:
    print(f'{event=}')
    return CommandEvent(**json.loads(json.dumps(dict_to_snake(event))))
