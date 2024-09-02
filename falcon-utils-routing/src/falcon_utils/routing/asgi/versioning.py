import falcon
import logging
from ..shared.utilities import find_responder, process_request

logger = logging.getLogger(__name__)


class APIVersioningMixin:

    @property
    def versioned_route(self):
        return True

    async def on_get(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        await process_request(responder, req, resp, *args, **kwargs)

    async def on_post(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        await process_request(responder, req, resp, *args, **kwargs)

    async def on_patch(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        await process_request(responder, req, resp, *args, **kwargs)

    async def on_put(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        await process_request(responder, req, resp, *args, **kwargs)

    async def on_head(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        await process_request(responder, req, resp, *args, **kwargs)

    async def on_delete(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        await process_request(responder, req, resp, *args, **kwargs)
