import falcon.asgi
import structlog
from collections.abc import Mapping
from typing import Any
from ..user import UserAPIProto

logger = structlog.get_logger("falcon.utils.auth")


class APIKeyAuthenticator:
    def __init__(self, header_name: str, api_keys: Mapping[str, Mapping[str, Any]]):
        self.__header_name = header_name
        self.__api_keys = api_keys

    async def __call__(
        self,
        user_cls: type[UserAPIProto],
        req: falcon.asgi.Request,
        resp: falcon.asgi.Response,
        *args,
        **kwargs
    ):
        api_key = req.get_header(self.__header_name)

        if not api_key:
            return False

        try:
            if not api_key in self.__api_keys:
                return False

            service_account = self.__api_keys[api_key]
            req.context.user = user_cls(
                id=service_account["name"], type="service-account", **service_account
            )
            return True
        except Exception as e:
            await logger.aerror(e)
            return False
