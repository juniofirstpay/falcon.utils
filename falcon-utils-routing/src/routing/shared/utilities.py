import falcon
from .constants import VERSIONING_HEADER_NAME, DEFAULT_VERSION

def find_responder(resource, req, header_name=VERSIONING_HEADER_NAME, default_version=DEFAULT_VERSION):
    header_value = req.headers.get(header_name, default_version)
    return getattr(resource, f"on_{req.method.lower()}_{header_value}", None)

def process_request(responder, req, resp, *args, **kwargs):
    if responder is None:
        resp.status = falcon.HTTP_NOT_IMPLEMENTED
        resp.complete = True
        return
    
    return callable(req, resp, *args, **kwargs)

async def process_request(responder, req, resp, *args, **kwargs):
    if responder is None:
        resp.status = falcon.HTTP_NOT_IMPLEMENTED
        resp.complete = True
        return
    
    return await callable(req, resp, *args, **kwargs)