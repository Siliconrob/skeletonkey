import json

from pydantic import ConfigDict, BaseModel

from RecordTypes.Credentials import Credentials
from RecordTypes.Keys import Keys


class CredentialsReply(BaseModel):
    credentials: Credentials
    key_pair: Keys

    model_config = ConfigDict(frozen=True, extra="forbid", validate_assignment=True)

    def __str__(self):
        return self.model_dump_json()

    def __repr__(self):
        return self.model_dump_json()