from dataclasses import dataclass


@dataclass
class NewUserToken:
    name: str | None
    value: str | None