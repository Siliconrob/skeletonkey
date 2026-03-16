import asyncio
import json
import os
import subprocess
import tempfile
import threading
import uuid
from collections import deque
from compression import zstd
from dataclasses import dataclass
from functools import wraps
from io import TextIOWrapper
from random import choice
from string import ascii_uppercase
from typing import Any, TypeVar, Callable, Tuple
from unittest.mock import MagicMock, patch

import databricks.sdk.service.iam as iam
import snowflake.connector as sc
from databricks.sdk import WorkspaceClient
from pydantic import SecretStr
from rich.console import Console
from snowflake.connector import SnowflakeConnection
from snowflake.connector.cursor import SnowflakeCursor

from RecordTypes.Credentials import Credentials
from RecordTypes.CredentialsReply import CredentialsReply
from RecordTypes.Keys import Keys
from RecordTypes.NewUserToken import NewUserToken
from RecordTypes.Step import DoSomething, StepStatus, build_steps
from RecordTypes.TestContext import TestContext
from RecordTypes.User import User as UserZ

console = Console()

from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T")



def get_connection_params() -> dict[str, str | None]:
    return dict(account=os.getenv("SNOWFLAKE_ACCOUNT"),
     user=os.getenv("SNOWFLAKE_USER"),
     private_key=os.getenv("SNOWFLAKE_PRIVATE_KEY"))


def result_set(cursor: SnowflakeCursor, cmd: str, init_fn: Callable[[Any], T]) -> deque[T]:
    result_list = deque()  # type: ignore[var-annotated]
    cursor.execute(cmd)
    for row in cursor:
        result_list.append(init_fn(row))
    return result_list


PEM_KEY_LENGTH = 4096





def create_public_private_keys(key_length: int = PEM_KEY_LENGTH) -> Keys:

    if os.name == 'nt': # No openssl on Windows by default
        return Keys(private=SecretStr(''.join(choice(ascii_uppercase) for i in range(PEM_KEY_LENGTH))),
                    public="public")

    key_file_base_name = "rsa_key"
    private_key_file_name = f"{key_file_base_name}.p8"
    public_key_file_name = f"{key_file_base_name}.pub"

    with tempfile.TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        ps1 = subprocess.run(["openssl", "genrsa", f"{key_length}"], universal_newlines=True, stdout=subprocess.PIPE)
        ps2 = subprocess.run(["openssl", "pkcs8", "-topk8", "-inform", "PEM", "-out", f"{private_key_file_name}", "-nocrypt"], input=ps1.stdout, universal_newlines=True, stdout=subprocess.PIPE)
        ps3 = subprocess.run(["openssl", "rsa", "-in", f"{private_key_file_name}", "-pubout", "-out", f"{public_key_file_name}"], universal_newlines=True, stdout=subprocess.PIPE)
        return Keys(private=SecretStr(extract_file_contents(os.path.join(tmp_dir, f'{private_key_file_name}'))),
                    public=extract_file_contents(os.path.join(tmp_dir, f'{public_key_file_name}')))


def extract_file_contents(file_path: str, read_lines: Callable[[TextIOWrapper], list[str]] = lambda z: z.readlines()) -> str:
    with open(file_path) as f:
        return "".join(x.strip().replace('\n', '') for x in read_lines(f))


def create_connection() -> sc.connection.SnowflakeConnection:
    return sc.connect(user=os.getenv("SNOWFLAKE_USER"),
                                       password=os.getenv("SNOWFLAKE_PAT"),
                                       account=os.getenv("SNOWFLAKE_ACCOUNT"))

def pat_action():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SHOW USERS LIKE '{os.getenv('SNOWFLAKE_USER')}'")
        current_data = cursor.fetchone()
        console.print(current_data)
        cursor.close()
        conn.close()
    return current_data


def public_key_cursor(connection_options: dict[str, str | None]) -> Callable[..., Any]:
    private_key = connection_options.get("private_key")
    account = connection_options.get("account")
    user = connection_options.get("user")

    if private_key is None:
        raise ValueError("Private key is not provided")
    if account is None:
        raise ValueError("Account is not provided")
    if user is None:
        raise ValueError("User is not provided")

    def inner_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable[..., Any]:
            with (tempfile.TemporaryDirectory() as tmp_dir, open(os.path.join(tmp_dir, uuid.uuid4().hex),
                                                                 "wb+") as tmp_key_file):
                tmp_key_file.write(private_key.encode('utf-8'))
                tmp_key_file.flush()
                conn_params = dict(account=account,
                                   user=user,
                                   authenticator='SNOWFLAKE_JWT',
                                   private_key_file=tmp_key_file.name)
                with (sc.connect(**conn_params) as conn, conn.cursor() as cursor):
                    return func(cursor, *args, **kwargs)
        return wrapper
    return inner_decorator


def public_key_connection(connection_options: dict[str, str | None]) -> SnowflakeConnection:

    private_key = connection_options.get("private_key")
    account = connection_options.get("account")
    user = connection_options.get("user")
    warehouse = connection_options.get("warehouse")

    def validate_input(input_text: str | None) -> bool:
        return input_text is not None and len(input_text.strip()) > 0

    invalid_params = []
    for k,v in dict(
        private_key=validate_input(private_key),
        account=validate_input(account),
        user=validate_input(user),
        # warehouse=validate_input(warehouse)
    ).items():
        if not v:
            invalid_params.append(f"No value for {k}")
    if len(invalid_params) > 0:
        raise ValueError(f"Missing connection parameters: {', '.join(invalid_params)}")

    with (tempfile.TemporaryDirectory() as tmp_dir, open(os.path.join(tmp_dir, uuid.uuid4().hex),
                                                         "wb+") as tmp_key_file):
        tmp_key_file.write(private_key.encode('utf-8'))  # type: ignore[union-attr]
        tmp_key_file.flush()
        conn_params = dict(account=account,
                           user=user,
                           authenticator='SNOWFLAKE_JWT',
                           # warehouse=warehouse,
                           private_key_file=tmp_key_file.name)
        return sc.connect(**conn_params)

def run_cmds(cmd: str) -> UserZ:
    # with (public_key_connection(get_connection_params()) as conn, conn.cursor() as cursor):
    conn = public_key_connection(get_connection_params())
    # with conn.cursor() as cursor:
    #     # time.sleep(150)
    #     cursor.execute("CALL SYSTEM$WAIT(1, 'MINUTES');")

    console.print(conn)
    with conn.cursor() as cursor:
        all_users = result_set(cursor, "SHOW USERS", lambda z: UserZ(*z))
        console.print(all_users)
        return all_users.popleft()


# @public_key_cursor(connection_options=get_connection_params())
def get_user(cursor: SnowflakeCursor, cmd: str) -> UserZ:
    users = result_set(cursor, cmd, lambda z: UserZ(*z))
    return users.popleft()


def certification_action() -> Tuple[UserZ, NewUserToken]:

    user_info = None
    token_info = None

    with (tempfile.TemporaryDirectory() as tmp_dir, open(os.path.join(tmp_dir, uuid.uuid4().hex), "wb+") as tmp_key_file):
        tmp_key_file.write(os.getenv("SNOWFLAKE_PRIVATE_KEY").encode('utf-8'))  # type: ignore[union-attr]
        tmp_key_file.flush()
        conn_params = connection_params(tmp_key_file.name)
        with (sc.connect(**conn_params) as conn, conn.cursor() as cursor):
            show_users_sql = f"SHOW USERS LIKE '{os.getenv('SNOWFLAKE_USER')}'"
            user_info = result_set(cursor, show_users_sql, lambda z: UserZ(*z)).popleft()
            if user_info is not None and user_info.created_on is not None:
                user_name = os.getenv('SNOWFLAKE_USER')
                new_token_name = f"{user_name}_token_{uuid.uuid4().hex}"
                add_new_pat = f"ALTER USER IF EXISTS {user_name} ADD PROGRAMMATIC ACCESS TOKEN {new_token_name} DAYS_TO_EXPIRY = 30 COMMENT = 'New token for {user_name}';"
                token_info = result_set(cursor, add_new_pat, lambda z: NewUserToken(*z)).popleft()
    return user_info, token_info  # type: ignore[return-value]


def connection_params(tmp_key_file_name: str) -> dict[str, str | None]:
    return dict(account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                authenticator='SNOWFLAKE_JWT',
                private_key_file=tmp_key_file_name)


def compress() -> None:
    new_keys = create_public_private_keys()
    a = zstd.compress(new_keys.private.get_secret_value().encode('utf-8'))  # type: ignore[union-attr]
    console.print(f'{len(a)=}')


    # return functools.partial(Callable, dbx_client, *args, **kwargs)

def ff_name(client: WorkspaceClient) -> iam.User:
    return client.users.get("abc")

def mocky() -> None:

    dbx_options = dict(host=os.getenv("DBX_HOST"),
               client_id=os.getenv("DBX_CLIENT_ID"),
               client_secret=os.getenv("DBX_CLIENT_SECRET"))

    with TestContext(dbx_options) as t:  # type: ignore[arg-type]

        try:
            result = t.get_dbx_value(t.dbx, lambda z: z.users.get("abc"))
        except Exception as e:
            print(e)

        helps = t.get_helper("normal")
        console.print(helps.echo_cmd())
        helps = t.get_helper("bah")
        console.print(helps.echo_cmd())

    fake_client = MagicMock(catalogs=MagicMock(list=MagicMock(return_value=["a", "b", "c"])))
    with (patch.object(TestContext, '_create_dbx_client', return_value=fake_client) as m,
          TestContext(dbx_options) as t):  # type: ignore[arg-type]

        for item in t.dbx.catalogs.list():
            console.print(item)

        help_mock = t.get_helper("help_normal")
        console.print(help_mock.echo_cmd())
        help_mock = t.get_helper("help_bah")
        console.print(help_mock.echo_cmd())


    console.print(m.call_count)


def dbx_connect():
    dbx = dict(host=os.getenv("DBX_HOST"),
               client_id=os.getenv("DBX_CLIENT_ID"),
               client_secret=os.getenv("DBX_CLIENT_SECRET"))

    w = WorkspaceClient(**dbx)
    for catalog in w.catalogs.list():
        console.print(catalog)

def class_test() -> Credentials:
    new_creds = Credentials(user_name="test_user", password=SecretStr("test_password"))
    console.print(new_creds)
    return new_creds

    return new_creds
    return dict(user_name=new_creds.user_name,
                password=f'{new_creds.password}')


async def main2() -> Any:

    step = DoSomething()
    step2 = DoSomething()
    step3 = DoSomething()
    step4 = DoSomething()
    step5 = DoSomething()
    current_step = build_steps(steps=[step, step2, step3, step4, step5])
    i = 0
    in_rollback = False
    while current_step is not None:
        try:
            force_failure = True if i == 2 else False
            if in_rollback:
                current_step = current_step.rollback()  # type: ignore[assignment]
                continue
            current_step = current_step.run(fail=force_failure)  # type: ignore[assignment]
        except Exception as e:
            in_rollback = True
            print(f"{current_step.id=}: {e=}")
        i += 1
    if in_rollback:
        print("Rollback complete")
    else:
        print("Steps completed successfully")


async def main() -> Any:
    # compress()
    mocky()
    return
    # dbx_connect()
    return class_test()

    return

    # pat_action()
    # results = certification_action()
    # console.print(results)
    find_user = f"SHOW USERS LIKE '{os.getenv('SNOWFLAKE_USER')}'"
    # user = get_user(find_user)
    # console.print(user)
    user2 = run_cmds(find_user)
    console.print(user2)
    # create_public_private_keys()

def handler(event: dict[str, Any], context: dict[str, Any]) -> dict[str, str] | CredentialsReply | str:
    try:
        console.print(event)
        console.print(context)
        new_keys = create_public_private_keys()
        test_data = class_test()
        reply = CredentialsReply(credentials=test_data, key_pair=new_keys)

        reply_text =str(reply)
        if event.get("showAllFields", False) is True:
            reply_text = repr(reply)
        return json.loads(reply_text)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    asyncio.run(main2())
    # asyncio.run(handler({}, {}))
