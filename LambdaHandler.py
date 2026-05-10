import json
from typing import Any

from camel_converter import dict_to_snake


def run_fn(event: dict[str, Any], context: dict[str, Any]) -> Any:
    print(f'{event=}')
    converted = dict_to_snake(event)
    return json.loads(converted)  # type: ignore[arg-type]
