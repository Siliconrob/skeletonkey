from databricks.sdk import WorkspaceClient
from databricks.sdk.service import catalog
import uuid
from datetime import datetime, timedelta, timezone
import os

w = WorkspaceClient()

current_time = datetime.now(timezone.utc)
expiration = timedelta(days=5)

print(expiration)

conn_options = dict(
    host=os.getenv('SNOWFLAKE_URL'),
    port=443,
    user=os.getenv("SNOWFLAKE_USER"),
    pem_private_key=decoded_key,
    sfWarehouse="SNOWFLAKE_LEARNING_WH",
    expires_in_secs=int(expiration.total_seconds())
)

conn_create = w.connections.create(
    comment="Public Key Connection",
    connection_type=catalog.ConnectionType.SNOWFLAKE,
    name=f'snowflake_{uuid.uuid4().hex}',
    options=conn_options,
)

catalog_options = dict(database="SNOWFLAKE_LEARNING_DB")
catalog_name = f'snow_{uuid.uuid4().hex}'
w.catalogs.create(name=catalog_name, connection_name=conn_create.name, options=catalog_options)


# cleanup
# w.connections.delete(name=conn_create.name)


from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64
import tempfile
import os
import uuid
from databricks.sdk import WorkspaceClient

dbx_client = WorkspaceClient()
result = dbx_client.secrets.get_secret("mystuff","accesskey")
current_key = base64.b64decode(result.value).splitlines('\n')  # type: ignore[arg-type]
current_key = b"".join(current_key[1:len(current_key)-1])  # type: ignore[assignment]
decoded_key = current_key.decode("utf-8")
# print(current_key)
print(decoded_key)