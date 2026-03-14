import json

from pydantic import SecretStr, BaseModel, ConfigDict, field_serializer


class Credentials(BaseModel):
    user_name: str
    password: SecretStr

    @field_serializer('password', mode='plain', return_type=str, when_used='json')  # type: ignore[call-overload]
    def serialize_password(self, value):
        return value.get_secret_value()

    model_config = ConfigDict(frozen=True, extra="forbid", validate_assignment=True)

    def __str__(self):
        return self.model_dump_json(exclude={'password'})

    def __repr__(self):
        return self.model_dump_json()