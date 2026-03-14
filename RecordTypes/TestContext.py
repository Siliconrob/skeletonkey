import warnings
from functools import wraps
from typing import Any, TypeVar, Callable

from databricks.sdk import WorkspaceClient
from rich.console import Console

console = Console()

class Helper:

    _options: dict[str, str | Any]
    _inputs: dict[str, str] = {}

    def __init__(self, options: dict[str,  str | Any]):
        self._options = options

    def echo_cmd(self) -> str:
        return ",".join([f'{k=}{v=}' for k,v in self._inputs.items()])

    def dbx_client(self) -> WorkspaceClient:
        return WorkspaceClient(**self._options)  # type: ignore[arg-type]

T = TypeVar("T")

class TestContext:

    _options: dict[str, str | Any]
    dbx: WorkspaceClient

    @staticmethod
    def get_dbx_value(dbx_client: WorkspaceClient,
                      run_fn: Callable[[WorkspaceClient], T],
                      default_value: T | None = None) -> T:
        @wraps(run_fn)
        def wrapper(*args, **kwargs):
            try:
                return run_fn(*args, **kwargs)
            except Exception:
                if default_value is not None:
                    warnings.warn(f"Failed to get {wrapper.__name__} from Databricks. Using default value.")
                    return default_value
                raise

        return wrapper(dbx_client)

    def get_helper(self, new_cmd: str) -> Helper:
        self._options[new_cmd] = new_cmd
        return Helper(self._options)

    def _create_dbx_client(self, input_options: dict[str, str | Any] | None = None) -> WorkspaceClient:
        if input_options is None:
            input_options = self._options
        return WorkspaceClient(**input_options)  # type: ignore[arg-type]

    def __init__(self, options: dict[str, str]):
        console.print("__init__")
        self._options = options

    def __enter__(self) -> "TestContext":
        console.print("__enter__")
        self.dbx = self._create_dbx_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dbx = None
        console.print("__exit__")

    def __repr__(self):
        console.print("__repr__")

    def __str__(self):
        console.print("__str__")