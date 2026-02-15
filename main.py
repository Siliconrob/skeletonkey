import asyncio
import os
import tempfile
import uuid
from typing import Any

import snowflake.connector as sc
from rich.console import Console

import RecordTypes

console = Console()

from dotenv import load_dotenv

load_dotenv()


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


def certification_action():
    with (tempfile.TemporaryDirectory() as tmp_dir, open(os.path.join(tmp_dir, uuid.uuid4().hex), "wb+") as tmp_key_file):
        tmp_key_file.write(os.getenv("SNOWFLAKE_PRIVATE_KEY").encode('utf-8'))
        tmp_key_file.flush()
        conn_params = method_name(tmp_key_file.name)
        with (sc.connect(**conn_params) as conn, conn.cursor() as cursor):
            cursor.execute(f"SHOW USERS LIKE '{os.getenv('SNOWFLAKE_USER')}'")
            current_data = cursor.fetchone()
            user_info = RecordTypes.User(*current_data)
            if user_info.has_pat:
                user_name = os.getenv('SNOWFLAKE_USER')
                new_token_name = f"{user_name}_token_{uuid.uuid4().hex}"
                add_new_pat = f"ALTER USER IF EXISTS {user_name} ADD PROGRAMMATIC ACCESS TOKEN {new_token_name} DAYS_TO_EXPIRY = 30 COMMENT = 'New token for {user_name}';"
                cursor.execute(add_new_pat)
                current_data = cursor.fetchone()
                new_token = RecordTypes.NewUserToken(*current_data)
                console.print(new_token)
            console.print(user_info)
        return current_data


def method_name(tmp_key_file_name: str) -> dict[str, str | None | Any]:
    return dict(account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                authenticator='SNOWFLAKE_JWT',
                private_key_file=tmp_key_file_name)

async def main() -> None:
    # pat_action()
    certification_action()


if __name__ == '__main__':
    asyncio.run(main())
