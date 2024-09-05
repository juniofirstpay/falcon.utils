from .wsgi.auth import Auth
from .asgi.auth import Auth as AsyncAuth
from .shared.config import AuthConfig


__all__ = ("Auth", "AsyncAuth")
