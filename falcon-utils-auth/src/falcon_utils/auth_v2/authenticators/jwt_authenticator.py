import falcon.asgi
import requests
import json
import jwt
import structlog
from typing import Literal, TypedDict, Any, cast, Optional

from ..user import UserAPIProto

logger = structlog.get_logger("falcon.utils.auth")

### types
type JWKSet = list[jwt.PyJWK]
type JWKSSourceType = Literal["url", "file", "str"]


class JWTDecodeOptions(TypedDict):
    verify_signature: bool
    require: list[str]
    verify_aud: bool
    verify_iss: bool
    verify_exp: bool
    verify_iat: bool
    verify_nbf: bool
    strict_aud: bool


# https://datatracker.ietf.org/doc/html/rfc7517#page-5
class JWKSDict(TypedDict):
    kty: Literal["EC", "RS"]
    kid: str
    use: Literal["sig", "enc"]
    alg: str
    n: Optional[str]
    e: Optional[str]
    x5c: Optional[list[str]]


#### methods
def validate(
    token: str,
    keys: JWKSet,
    algorithms: list[str],
    options: JWTDecodeOptions,
    audience: str = None,
    issuer: str = None,
    leeway: float = None,
) -> dict[str, Any]:
    claims: Optional[dict] = None

    kwargs = {}
    if audience:
        kwargs.update(audience=audience)
    if issuer:
        kwargs.update(issuer=leeway)
    if leeway:
        kwargs.update(leeway=leeway)
    for key in keys:
        try:
            claims = jwt.decode(token, key, algorithms, options, **kwargs)
        except jwt.exceptions.PyJWTError:
            pass

    if claims is None:
        raise Exception()

    return claims


def load_jwks(data: list[JWKSDict]) -> JWKSet:
    keys: JWKSet = []
    for item in data:
        keys.append(jwt.PyJWK.from_dict(item, item["alg"]))

    return keys


def load_jwks_remote(url: str) -> list[JWKSDict]:
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(e)


def load_jwks_file(path: str):
    with open(path, "r") as file:
        return json.loads(file)


### classes
class JWTAuthenticator:

    def __init__(
        self,
        header_name: str,
        decoding_options: JWTDecodeOptions,
        jwks_sources: dict[JWKSSourceType, str],
        issuer: str = None,
        audience: str = None,
        leeway: float = None,
    ):
        self.__header_name = header_name
        self.__decoding_options = decoding_options
        self.__jwks_sources = jwks_sources
        self.__issuer = issuer
        self.__audience = audience
        self.__leeway = leeway

        self.__setup()

    def __setup(self):
        jwks: list[JWKSDict] = []
        for source_type, source_value in self.__jwks_sources.items():
            if source_type == "str":
                jwks += cast(list[dict[str, Any]], json.loads(source_value))
            elif source_type == "file":
                jwks += load_jwks_file(source_value)
            elif source_type == "url":
                jwks += load_jwks_remote(source_value)

        self.__jwkset = load_jwks(jwks)
        self.__algorithms = list(map(lambda x: x["alg"], jwks))

    def validate(self, token: str):
        return validate(
            token,
            self.__jwkset,
            self.__algorithms,
            self.__decoding_options,
            issuer=self.__issuer,
            audience=self.__audience,
            leeway=self.__leeway,
        )

    async def __call__(
        self,
        user_cls: type[UserAPIProto],
        req: falcon.asgi.Request,
        resp: falcon.asgi.Response,
        *args,
        **kwargs,
    ):
        token = req.get_header(self.__header_name)

        if token:
            try:
                claims = self.validate(token)
                req.context.user = user_cls(id=claims.get("sub"), type="user", **claims)
                return True
            except Exception as e:
                await logger.aerror(e)
                return False
        else:
            return False


__all__ = ("JWTAuthenticator",)
