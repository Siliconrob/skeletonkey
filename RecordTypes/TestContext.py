from rich.console import Console

console = Console()

class Helper:

    def __init__(self, options: dict[str, str]):
        self._options = options

    def echo_cmd(self) -> str:
        return ",".join([f'{k=}{v=}' for k,v in self._options.items()])

class TestContext:

    _options: dict[str, str]

    def get_helper(self, new_cmd: str) -> Helper:
        self._options[new_cmd] = new_cmd
        return Helper(self._options)

    def __init__(self, options: dict[str, str]):
        console.print("__init__")
        self._options = options

    def __enter__(self):
        console.print("__enter__")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        console.print("__exit__")

    def __repr__(self):
        console.print("__repr__")

    def __str__(self):
        console.print("__str__")