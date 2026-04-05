import os

import pytest
from pydantic import SecretStr

from RecordTypes.Credentials import Credentials
from rich.console import Console
console = Console()

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


def test_credentials_input():
    creds = Credentials(user_name="user", password=SecretStr("password"))
    assert str(creds.password) == '**********'


@pytest.mark.skipif(IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions.")
def test_works_local_only():
    console.print("This test only works locally.")
    assert True