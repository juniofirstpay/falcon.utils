from typing import Tuple, Union
from dataclasses import dataclass
from .user import Anonymous, User
from .constants import AuthSchemes

from collections import namedtuple

Credentials = namedtuple("Credentials", ["type", "value"])


@dataclass(init=True)
class RequestAuthContext:
    user: Union[Anonymous, User]
    credentials: Credentials = None
