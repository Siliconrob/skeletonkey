from typing import Any

from LambdaHandler import run_fn


def str_handler() -> None:
    text = "//jjja;"
    text = text.removesuffix("/").removeprefix("/")
    print(text)



def handler(event: dict[str, Any], context: dict[str, Any]) -> Any:
    return run_fn(event, context)


if __name__ == "__main__":
    # str_handler()

    event = {
    "cmd": "databricks",
    "subCommand": "help",
    "args": {
        "showAll": True,
        "userId": None
    }
}

    z = handler(event, {})
    print(f'{z=}')
    # asyncio.run(str_handler())
    # asyncio.run(main2())
    # asyncio.run(handler({}, {}))
    # handler_alt({}, {})
    # handler({}, {})
