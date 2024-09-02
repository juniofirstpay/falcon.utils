from typing import Optional
from dataclasses import dataclass


@dataclass(init=True, frozen=True)
class User:
    ref: str
    domain: Optional[str]
