import falcon
import logging
from ..shared.utilities import find_responder, process_request

logger = logging.getLogger(__name__)


class APIVersioningMixin:

    @property
    def versioned_route(self):
        return True

    def on_get(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        process_request(responder, req, resp, *args, **kwargs)

    def on_post(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        process_request(responder, req, resp, *args, **kwargs)

    def on_patch(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        process_request(responder, req, resp, *args, **kwargs)

    def on_put(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        process_request(responder, req, resp, *args, **kwargs)

    def on_head(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        process_request(responder, req, resp, *args, **kwargs)

    def on_delete(self, req: falcon.Request, resp: falcon.Response, *args, **kwargs):
        responder = find_responder(self, req)
        process_request(responder, req, resp, *args, **kwargs)
