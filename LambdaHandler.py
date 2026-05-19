import dataclasses
import json
from copy import deepcopy
from typing import Any, TypeVar

from camel_converter import dict_to_snake


T = TypeVar("T")

def update_values(current: T, **kwargs) ->  T:
    if not dataclasses.is_dataclass(current):
        raise TypeError("Input must be a dataclass")
    z = dataclasses.replace(current, **kwargs)  # type: ignore[type-var]

    f = dataclasses.asdict(z)

    return T.__init__(**f)


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

    converted = dict_to_snake(event)
    args = CommandEventArgs(**converted.get("args", {}))
    pop = CommandEvent(sub_command=converted.get("sub_command"), cmd=converted.get("cmd"), args=args)

    k = dataclasses.asdict(pop)
    k["args"]['show_all'] = False
    

    # jj = dataclasses.replace(pop, args=dataclasses.replace(pop.args, show_all=False))

    cmd = CommandEvent(**json.loads(json.dumps(dict_to_snake(event))))

    h = dict(abc=1)
    try:
        h2 = update_values(h, abc=2)
    except TypeError as e:
        print(e)

    modded = dataclasses.replace(cmd, sub_command="abc")
    j = CommandEventArgs(**cmd.args)
    new_args = dataclasses.replace(j, show_all=False)
    mod2 = dataclasses.replace(cmd, args=new_args)


    # modded = update_values(cmd, sub_command="abc")
    return modded

