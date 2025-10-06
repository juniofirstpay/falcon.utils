import falcon.asgi
import structlog
from typing import Optional
from collections.abc import Callable, Coroutine
from collections import OrderedDict
from .user import UserAPIProto

logger = structlog.get_logger("falcon.utils.auth")

type AuthenticationCallback = Callable[
    [type[UserAPIProto], falcon.asgi.Request, falcon.asgi.Response],
    Coroutine[None, None, bool],
]


class Authentication:

    def __init__(self, user_cls: type[UserAPIProto]):
        self.__authenticators: OrderedDict[str, AuthenticationCallback] = OrderedDict()
        self.__user_cls = user_cls

    def add_authenticator(
        self, auth_scheme: str, authenticator: AuthenticationCallback
    ):
        if self.__authenticators.get(auth_scheme):
            logger.awarn("authenticator already added with the scheme %s", auth_scheme)
        self.__authenticators[auth_scheme] = authenticator

    def authenticate(self, allowed_auth_schemes: Optional[list[str]] = None):
        if allowed_auth_schemes:
            allowed_authenticators = list(
                filter(
                    lambda x: x[0] in allowed_auth_schemes,
                    self.__authenticators.items(),
                )
            )
        else:
            allowed_authenticators = list(self.__authenticators.items())

        async def authentication_hook(
            req: falcon.asgi.Request, resp: falcon.asgi.Response, *args, **kwargs
        ):
            authenticated = False
            for auth_scheme, authenticator in allowed_authenticators:

                await logger.adebug("authenticating request with %s", auth_scheme)

                try:
                    authenticated = await authenticator(
                        self.__user_cls, req, resp, *args, **kwargs
                    )
                except Exception as e:
                    await logger.aerror(
                        "error occured with authentication scheme %s", auth_scheme
                    )
                    await logger.aerror(e)

                    raise falcon.HTTPError(falcon.HTTPServiceUnavailable)

                if authenticated:
                    # current authenticator has sucessfully authenticated
                    # the request, no other authenticator shall be tried
                    break

            if not authenticated:
                # none of the authenticators were able to
                # successfully authenticate the request
                raise falcon.HTTPError(falcon.HTTP_401)

        return authentication_hook
