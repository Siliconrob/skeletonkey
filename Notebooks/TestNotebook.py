# Databricks notebook source
# MAGIC %pip install snowflake-connector-python
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import json
import boto3
from databricks.sdk import WorkspaceClient
import base64

try:
    w = WorkspaceClient()
    access_key = base64.b64decode(w.secrets.get_secret("aws", "key").value).decode(
        "utf-8"
    )
    access_value = base64.b64decode(w.secrets.get_secret("aws", "value").value).decode(
        "utf-8"
    )
    data = base64.b64decode(w.secrets.get_secret("aws", "message").value).decode(
        "utf-8"
    )

    message = json.loads(data)
    message_text = json.dumps(message)

    sns = boto3.client(
        "sns",
        region_name="us-east-1",
        aws_access_key_id=access_key,
        aws_secret_access_key=access_value,
    )
    sns.publish(
        TopicArn=os.getenv("SNS_TOPIC_ARN"),
        Message=message_text,
        Subject="Happy Times",
    )
except Exception as e:
    print(f"{e=}")
