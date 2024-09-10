from typing import List, Dict, Union
from dataclasses import dataclass
from .constants import AuthSchemes

__all__ = ("AuthConfig",)


@dataclass(init=True)
class AuthConfig:
    schemes: List[AuthSchemes]  # list of enabled schemes
    api_keys: Dict[str, str]
    headers: Dict[AuthSchemes, List[str]]
    authorization_model: str = None
    authorization_policy: str = None
    jwks: List[Union[str, Dict]] = None
