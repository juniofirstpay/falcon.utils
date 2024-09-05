from enum import Enum

__all__ = ("AuthSchemes",)


class AuthSchemes(int, Enum):
    BASIC = 1
    TOKEN = 2
    JWT = 3
    API_KEY = 4


class UserType(int, Enum):
    anonymous = 0
    user = 1
    service = 2
