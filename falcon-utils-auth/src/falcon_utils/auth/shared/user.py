from dataclasses import dataclass
from .constants import UserType

__all__ = (
    "Anonymous",
    "User",
)


@dataclass(init=True)
class Anonymous:
    domain: str
    authenticated = False
    ref: str = "anonymous"
    type: UserType = UserType.anonymous


@dataclass(init=True)
class User:
    domain: str
    ref: str
    type: UserType
    extras: dict
    authenticated: bool = True
