from typing import Union

__all__ = "get_domain"


def get_domain(req: Union["falcon.Request", "falcon.asgi.Request"]):
    host = req.get_header("host")
    forwarded_host = req.get_header("x-forwarded-host")
    return forwarded_host or host
