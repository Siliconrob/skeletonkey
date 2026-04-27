import dataclasses

from pydantic import ConfigDict, BaseModel, Field

from RecordTypes.Credentials import Credentials, CredentialsAlt
from RecordTypes.Keys import Keys, KeysAlt


@dataclasses.dataclass(frozen=True)
class CredentialsReplyAlt:
    credentials: CredentialsAlt
    key_pair: KeysAlt

class CredentialsReply(BaseModel):
    credentials: Credentials # = Field(exclude=True, repr=False, json_schema_extra={"exclude": True})
    key_pair: Keys

    model_config = ConfigDict(frozen=True, extra="forbid", validate_assignment=True)

    def __str__(self):
        return self.model_dump_json(
            exclude={"credentials": {"password"}, "key_pair": {"private"}}
        )

    def __repr__(self):
        return self.model_dump_json()
