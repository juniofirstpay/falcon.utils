import falcon
from .constants import VERSIONING_HEADER_NAME, DEFAULT_VERSION

def find_responder(resource, req: falcon.Request, header_name=VERSIONING_HEADER_NAME, default_version=DEFAULT_VERSION):
    header_value = req.headers.get(header_name.lower(), None) or req.headers.get(header_name.upper(), None) or default_version
    return getattr(resource, f"on_{req.method.lower()}_{header_value}", None)

def process_request(responder, req, resp, *args, **kwargs):
    if responder is None:
        resp.status = falcon.HTTP_NOT_IMPLEMENTED
        resp.complete = True
        return
    
    return responder(req, resp, *args, **kwargs)

async def process_request(responder, req, resp, *args, **kwargs):
    if responder is None:
        resp.status = falcon.HTTP_NOT_IMPLEMENTED
        resp.complete = True
        return
    
    return await responder(req, resp, *args, **kwargs)