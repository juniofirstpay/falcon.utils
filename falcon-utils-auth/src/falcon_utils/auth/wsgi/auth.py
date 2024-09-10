import falcon
import falcon.asgi

from typing import TypeVar

from ..shared.config import AuthConfig
from ..shared.context import RequestAuthContext, Credentials
from ..shared.user import Anonymous, User
from ..shared.constants import AuthSchemes, UserType
from ..shared.jwt import JWTAuth
from ..utils import get_domain
from ..casbin import create_enforcer
from .middleware import Middleware


Request = TypeVar("Request", falcon.Request, falcon.asgi.Request)
Response = TypeVar("Response", falcon.Response, falcon.asgi.Response)

ERR_CREDENTIALS_INVALID = "invalid credentials"



        
            
        

class Auth:

    def __init__(self, config: AuthConfig):
        self._config = config
        if self._config.authorization_model and self._config.authorization_policy:
            self._enforcer = create_enforcer(
                self._config.authorization_model, 
                self._config.authorization_policy,
                True
            )

        if AuthSchemes.JWT in self._config.schemes:
            self._jwt_auth = JWTAuth(url=self._config.jwks[0], headers=self._config.jwks[1])

    @property
    def middleware(self):
        return Middleware(self, self._config)

    def _check_conflict(self, req: Request):
        context = req.context.auth

        for scheme in self._config.schemes:
            header_names = self._config.headers.get(scheme) or []
            for header_name in header_names:
                credential_value = req.get_header(header_name, None)
                if credential_value:
                    if context.credentials:
                        return True
                    context.credentials = Credentials(
                        AuthSchemes(scheme), credential_value
                    )

        return False

    def prepare(self, req: Request):
        """
        associates a context object to the request context
        """
        req.context.auth = RequestAuthContext(
            user=Anonymous(domain=get_domain(req)), credentials=None
        )

    def _context(self, req: Request) -> RequestAuthContext:
        return req.context.auth

    def _authenticate_with_api_key(self, req: Request, context: RequestAuthContext):
        api_key_value = context.credentials.value

        # implement credentials hashing
        client_id = self._config.api_keys.get(api_key_value)

        if client_id is None:
            raise Exception(ERR_CREDENTIALS_INVALID)

        context.user = User(
            authenticated=True,
            type=UserType.service,
            ref=client_id,
            domain=context.user.domain,
            extras={},
        )

    def _authenticate_with_oauth(self, req, Request, context: RequestAuthContext):
        pass

    def _authenticate_with_jwt(self, req: Request, context: RequestAuthContext):
        payload = self._jwt_auth.validate(context.credentials.value)
        context.user = User(
            authenticated=True,
            type=UserType.service,
            ref=payload["user_id"],
            domain=context.user.domain,
            extras={
                **payload
            },
        )


    def validate(self, req: Request):
        context = self._context(req)

        print("context", context)

        if len(self._config.schemes) == 0:
            return True  # by default anonymous schemes are enabled

        if context.credentials is None:
            return True

        try:
            if context.credentials.type == AuthSchemes.API_KEY:
                self._authenticate_with_api_key(req, context)
            elif context.credentials.type == AuthSchemes.TOKEN:
                self._authenticate_with_oauth(req, context)
            elif context.credentials.type == AuthSchemes.JWT:
                print(req, context)
                self._authenticate_with_jwt(req, context)
        except Exception as e:
            if str(e) == ERR_CREDENTIALS_INVALID:
                return False
            else:
                raise e

        return True

    def verify(self, req: Request, auth: bool):
        context = self._context(req)

        if auth == True and isinstance(context.user, Anonymous):
            return False

        return True

    def authenticate(self, auth=True):
        def wrapped_hook(req: "falcon.Request", resp: "falcon.Response", *args):
            verified = self.verify(req, auth)
            if not verified:
                resp.status = falcon.HTTP_401
                resp.complete = True

        return wrapped_hook

    def authorize(self, obj: str = None, act: str = None):
        def wrapped_hook(req: "falcon.Request", resp: "falcon.Response", *args):
            # https://falcon.readthedocs.io/en/stable/api/request_and_response_wsgi.html#id1
            context: RequestAuthContext = req.context.auth
            # user: User = req.context.auth

            _obj = obj
            _act = act
            _dom = context.user.domain

            if _obj is None:
                _obj = req.path

            if _act is None:
                _act = req.method

            if _dom is None:
                _dom = req.host

            if not self._enforcer.enforce(context.user.ref, _dom, _obj, _act):
                resp.status = falcon.HTTP_403
                resp.complete = True

        return wrapped_hook
