from pydantic import BaseModel, SecretStr, ConfigDict, field_serializer


class Keys(BaseModel):
    private: SecretStr
    public: str

    @field_serializer("private", mode="plain", return_type=str, when_used="json")
    def serialize_private_key(self, value):
        return value.get_secret_value()

    model_config = ConfigDict(frozen=True, extra="forbid", validate_assignment=True)

    def __str__(self):
        return self.model_dump_json(exclude={"private"})

    def __repr__(self):
        return self.model_dump_json()
