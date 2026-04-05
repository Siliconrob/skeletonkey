import pytest
from pydantic import SecretStr

from RecordTypes.Credentials import Credentials


def test_credentials_input():
    creds = Credentials(user_name="user", password=SecretStr("password"))
    assert str(creds.password) == '**********'


