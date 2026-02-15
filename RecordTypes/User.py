import ast
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


@dataclass
class User:
    name: str
    created_on: datetime | None = None
    login_name: str | None = None
    display_name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    mins_to_unlock: int | None = None
    days_to_expiry: int | None = None
    comments: str | None = None
    disabled: bool | None = False
    must_change_password: bool = False
    snowflake_lock: bool = False
    default_warehouse: str | None = None
    default_namespace: str | None = None
    default_role: str | None = None
    default_secondary_roles: list[str] | None = field(default_factory=list[str])
    ext_authn_duo: bool | None = False
    ext_authn_uid: str | None = None
    mins_to_bypass_mfa: int | None = None
    owner: str | None = None
    last_successful_login: datetime | None = None
    expires_at_time: datetime | None = None
    locked_until_time: datetime | None = None
    has_password: bool | None = False
    has_rsa_public_key: bool | None = False
    type: str | None = None
    has_mfa: bool | None = False
    has_pat: bool | None = False
    has_workload_identity: bool | None = False
    is_from_organization_user: bool | None = False

    def _parse_bool(self, property_name: str, parse_fn: Callable[[str], bool] = lambda x: x.lower() in ("true", "1")) -> None:
        current_value = getattr(self, property_name, None)
        if current_value is not None:
            setattr(self, property_name, parse_fn(current_value))

    def _parse_int(self, property_name: str, parse_fn: Callable[[str], int] = lambda x: int(x)) -> None:
        current_value = getattr(self, property_name, None)
        if current_value is not None:
            setattr(self, property_name, parse_fn(current_value))

    def __post_init__(self):
        self._parse_bool("has_pat")
        self._parse_bool("has_mfa")
        self._parse_bool("has_workload_identity")
        self._parse_bool("is_from_organization_user")
        self._parse_bool("disabled")
        self._parse_bool("has_password")
        self._parse_bool("has_rsa_public_key")
        self._parse_bool("ext_authn_duo")

        self._parse_int("mins_to_unlock")
        self._parse_int("days_to_expiry")
        self._parse_int("mins_to_bypass_mfa")

        if self.default_secondary_roles is not None:
            self.default_secondary_roles = ast.literal_eval(self.default_secondary_roles)


