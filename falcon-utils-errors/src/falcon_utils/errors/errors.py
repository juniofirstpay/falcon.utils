import falcon
import falcon.asgi
import typing
import json
import collections

__all__ = (
    "ErrorCode",
    "Error",
    "ErrorRegistry",
    "add_error_handler",
)

ErrorCode = collections.namedtuple("ErrorCode", ["code", "category", "message"])

class Error(Exception):
    
    def __init__(self, code: ErrorCode, extras=None, status: falcon.HTTPStatus = falcon.HTTP_500):
        self.__code = code
        self.__extras = extras
        self.__http_status = status
        super(Error, self).__init__(self.__code.message)
    
    @property
    def http_status(self):
        return self.__http_status
    
    def to_dict(self):
        return {
            'code': self.__code.code,
            'category': self.__code.category,
            'description': self.__code.message,
            'extras': self.__extras,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class ErrorRegistry(dict):
    
    def __init__(self):
        self.__errors: typing.Dict[str, ErrorCode] = {}
    
    def register(self, error_code: ErrorCode):
        self.__errors[error_code.code] = error_code

    def __getattribute__(self, name: str) -> typing.Any:
        if self.__errors.get(name):
            return self.__errors[name]
        return super().__getattribute__(name)
    
def add_error_handler(app: typing.Union["falcon.asgi.App", "falcon.App"], asgi=False):
    if asgi == True:
        async def handler(req: falcon.asgi.Request, resp: falcon.asgi.Response, ex: Error, params, **kwargs):
            resp.status = ex.http_status
            resp.media = {
                'status': None,
                'data': None,
                'error': ex.to_dict()
            }
    else:
        def handler(req: falcon.Request, resp: falcon.Response, ex: Error, params, **kwargs):
            resp.status = ex.http_status
            resp.media = {
                'status': None,
                'data': None,
                'error': ex.to_dict()
            }
        
    app.add_error_handler(Error, handler)