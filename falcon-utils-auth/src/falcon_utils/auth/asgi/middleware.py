import falcon
from falcon.asgi import Request, Response
from ..shared.config import AuthConfig
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class Middleware:

    def __init__(self, auth, config: AuthConfig):
        self._auth = auth
        self._config = config

    async def process_request(self, req: Request, resp: Response, *args, **kwargs):
        # initiliazes auth context for a request
        self._auth.prepare(req)

        has_conflict = await self._auth._check_conflict(req)
        if has_conflict:
            # multiple authentication methods being used in the request
            resp.status = falcon.HTTP_409
            resp.complete = True
            return

        authenticated = await self._auth.validate(req)
        
        logger.info(f"AUTHENTICATED: {authenticated}")
        
        if authenticated == False:
            resp.status = falcon.HTTP_401
            resp.complete = True
            return

    async def process_resource(self, req: Request, resp: Response, resource, params):
        # if hasattr(resource, "_auth", False):
        #     await self.verify(req, resp, resource._auth)
        pass

    async def process_response(
        self, req: Request, resp: Response, resource, req_succeeded: bool
    ):
        pass
