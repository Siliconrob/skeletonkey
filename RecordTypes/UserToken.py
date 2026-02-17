from dataclasses import dataclass
from datetime import datetime


@dataclass
class UserToken:
    name: str | None
    user_name: str | None
    role_restriction: str | None
    expires_at: datetime | None
    status: str | None
    comments: str | None
    created_on: datetime | None
    created_by: str | None
    mins_to_bypass_network_policy_requirement: int | None
    rotated_to: str | None

    def __post_init__(self):
        if self.mins_to_bypass_network_policy_requirement is not None:
            self.mins_to_bypass_network_policy_requirement = int(self.mins_to_bypass_network_policy_requirement)