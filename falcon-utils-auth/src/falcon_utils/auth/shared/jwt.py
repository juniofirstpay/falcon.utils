
import asyncio
from typing import List, Union
from jwt import PyJWK, PyJWKSet, PyJWKClient as _PyJWKClient, PyJWKClientError, decode
from jwt.api_jwt import decode_complete as decode_token

__all__ = ("get_jwkset_from_json", "get_jwkset_from_remote",)

async def get_jwkset_from_remote(url: str) -> PyJWKSet:
    client = PyJWKClient(uri=url, cache_keys=True, max_cached_keys=30, lifespan=300)
    await asyncio.to_thread(client.fetch_data)
    return client.get_jwk_set()

async def get_jwkset_from_json(data: Union[str, dict]) -> PyJWKSet:
    if isinstance(data, str):
        return PyJWKSet.from_json(data)
    return PyJWKSet.from_dict(data)


class PyJWKClient(_PyJWKClient):

    async def fetch_data_async(self):
        return await asyncio.to_thread(self.fetch_data)

    async def get_jwk_set_async(self, refresh: bool = False) -> PyJWKSet:
        data = None
        if self.jwk_set_cache is not None and not refresh:
            data = self.jwk_set_cache.get()

        if data is None:
            data = await self.fetch_data_async()

        if not isinstance(data, dict):
            raise PyJWKClientError("The JWKS endpoint did not return a JSON object")

        return PyJWKSet.from_dict(data)

    async def get_signing_keys_async(self, refresh: bool = False) -> List[PyJWK]:
        jwk_set = self.get_jwk_set_async(refresh)
        signing_keys = [
            jwk_set_key
            for jwk_set_key in jwk_set.keys
            if jwk_set_key.public_key_use in ["sig", None] and jwk_set_key.key_id
        ]

        if not signing_keys:
            raise PyJWKClientError("The JWKS endpoint did not contain any signing keys")

        return signing_keys

    async def get_signing_key_async(self, kid: str) -> PyJWK:
        signing_keys = await self.get_signing_keys_async()
        signing_key = await self.match_kid(signing_keys, kid)

        if not signing_key:
            # If no matching signing key from the jwk set, refresh the jwk set and try again.
            signing_keys = await self.get_signing_keys_async(refresh=True)
            signing_key = await self.match_kid(signing_keys, kid)

            if not signing_key:
                raise PyJWKClientError(
                    f'Unable to find a signing key that matches: "{kid}"'
                )

        return signing_key

    async def get_signing_key_from_jwt_async(self, token: str) -> PyJWK:
        unverified = decode_token(token, options={"verify_signature": False})
        header = unverified["header"]
        return await self.get_signing_key_async(header.get("kid"))
    

class JWTAuth:
    
    def __init__(self, url: str=None, headers: dict=None, is_async=False):
        self.__is_async = is_async
        self.__jwk_client = PyJWKClient(uri=url, headers=(headers or {}), cache_keys=True, cache_jwk_set=True, lifespan=3600)
        
    def validate(self, token: str):
        signing_key = self.__jwk_client.get_signing_key_from_jwt(token)
        payload = decode(token, signing_key, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    
    async def validate_async(self, token: str):
        signing_key = await self.__jwk_client.get_signing_key_from_jwt_async(token)
        payload = decode(token, signing_key, algorithms=["RS256"], options={"verify_aud": False})
        return payload

    def fetch_keys(self):
        self.__jwk_client.fetch_data()
    
    def fetch_keys_async(self):
        self.__jwk_client.fetch_data_async()

    @staticmethod
    async def init(url: str):
        auth = JWTAuth(url)
        auth.fetch_keys()
        return auth
    
    @staticmethod
    async def init_async(url: str):
        auth = JWTAuth(url, is_async=True)
        await auth.fetch_keys_async()
        return auth