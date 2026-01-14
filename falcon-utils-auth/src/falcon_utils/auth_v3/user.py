from typing import Any, Protocol


class UserAPIProto[T, U](Protocol):
    def __init__(self, id: T, type: U, **kwargs):
        self.__id = id
        self.__type = type
        self.__kwargs = kwargs

    @property
    def id(self) -> T:
        return self.__id

    @property
    def type(self) -> U:
        return self.__type

    def get(self, key: str):
        return self.__kwargs.get(key)


__all__ = ("User",)
