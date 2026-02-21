import asyncio
import functools
import os
import tempfile
import uuid
from collections import deque
from functools import wraps
from typing import Any, TypeVar, Callable, Tuple

import snowflake.connector as sc
from rich.console import Console
from snowflake.connector.cursor import SnowflakeCursor

from RecordTypes.NewUserToken import NewUserToken
from RecordTypes.User import User

console = Console()

from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T")


def result_set(cursor: SnowflakeCursor, cmd: str, init_fn: Callable[[Any], T]) -> deque[T]:
    result_list = deque()  # type: ignore[var-annotated]
    cursor.execute(cmd)
    for row in cursor:
        result_list.append(init_fn(row))
    return result_list


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


def with_public_key(private_key_name: str) -> Callable[..., Any]:
    key_value = os.getenv(private_key_name).encode('utf-8')  # type: ignore[union-attr]
    def inner_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs) -> Callable[..., Any]:
            with (tempfile.TemporaryDirectory() as tmp_dir, open(os.path.join(tmp_dir, uuid.uuid4().hex),
                                                                 "wb+") as tmp_key_file):
                tmp_key_file.write(key_value)
                tmp_key_file.flush()
                conn_params = connection_params(tmp_key_file.name)
                with (sc.connect(**conn_params) as conn, conn.cursor() as cursor):
                    return func(cursor, *args, **kwargs)
        return wrapper
    return inner_decorator


@with_public_key("SNOWFLAKE_PRIVATE_KEY")
def get_user(cursor: SnowflakeCursor, cmd: str) -> User:
    users = result_set(cursor, cmd, lambda z: User(*z))
    return users.popleft()


def certification_action() -> Tuple[User, NewUserToken]:

    user_info = None
    token_info = None

    with (tempfile.TemporaryDirectory() as tmp_dir, open(os.path.join(tmp_dir, uuid.uuid4().hex), "wb+") as tmp_key_file):
        tmp_key_file.write(os.getenv("SNOWFLAKE_PRIVATE_KEY").encode('utf-8'))  # type: ignore[union-attr]
        tmp_key_file.flush()
        conn_params = connection_params(tmp_key_file.name)
        with (sc.connect(**conn_params) as conn, conn.cursor() as cursor):
            show_users_sql = f"SHOW USERS LIKE '{os.getenv('SNOWFLAKE_USER')}'"
            user_info = result_set(cursor, show_users_sql, lambda z: User(*z)).popleft()
            if user_info is not None and user_info.created_on is not None:
                user_name = os.getenv('SNOWFLAKE_USER')
                new_token_name = f"{user_name}_token_{uuid.uuid4().hex}"
                add_new_pat = f"ALTER USER IF EXISTS {user_name} ADD PROGRAMMATIC ACCESS TOKEN {new_token_name} DAYS_TO_EXPIRY = 30 COMMENT = 'New token for {user_name}';"
                token_info = result_set(cursor, add_new_pat, lambda z: NewUserToken(*z)).popleft()
    return user_info, token_info  # type: ignore[return-value]


def connection_params(tmp_key_file_name: str) -> dict[str, str | None | Any]:
    return dict(account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                authenticator='SNOWFLAKE_JWT',
                private_key_file=tmp_key_file_name)

async def main() -> None:
    # pat_action()
    # results = certification_action()
    # console.print(results)
    user = get_user(f"SHOW USERS LIKE '{os.getenv('SNOWFLAKE_USER')}'")
    console.print(user)


if __name__ == '__main__':
    asyncio.run(main())
