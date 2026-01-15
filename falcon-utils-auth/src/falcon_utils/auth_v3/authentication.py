import falcon.asgi
import structlog
from typing import TypeVar, TypeAlias
from collections.abc import Callable, Coroutine, Iterable
from collections import OrderedDict

logger = structlog.get_logger("falcon.utils.auth")

T = TypeVar("T")

AuthenticationCallback: TypeAlias = Callable[
    [type[T], falcon.asgi.Request, falcon.asgi.Response],
    Coroutine[None, None, bool],
]


class Authentication:

    def __init__(self, user_cls: type[T]):
        self.__authenticators: OrderedDict[str, AuthenticationCallback] = OrderedDict()
        self.__user_cls = user_cls

    def add_authenticator(
        self, auth_scheme: str, authenticator: AuthenticationCallback
    ):
        if self.__authenticators.get(auth_scheme):
            logger.awarn("authenticator already added with the scheme %s", auth_scheme)
        self.__authenticators[auth_scheme] = authenticator

    async def authenticate(
        self,
        req: falcon.asgi.Request,
        resp: falcon.asgi.Response,
        resource,
        params,
        *,
        allowed_auth_schemes: Iterable[str] | None = None,
        **kwargs,
    ):
        if not allowed_auth_schemes:
            return

        authenticated = False
        for auth_scheme in allowed_auth_schemes:
            if (authenticator := self.__authenticators.get(auth_scheme)) is None:
                break

            await logger.adebug("authenticating request with %s", auth_scheme)

            try:
                authenticated = await authenticator(self.__user_cls, req, resp)
            except Exception as e:
                await logger.awarn(
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
