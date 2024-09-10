import falcon.asgi
from src.falcon_utils.compression import Middleware

def read_large_file():
    with open('./large-file.json', 'rb') as file:
        return file.read()

class CompressionRoute:
    async def on_get(self, req, resp: falcon.asgi.Response, **kwargs):        
        try:
            resp.data = read_large_file()
        except Exception as e:
            print(e)

class NormalRoute:
    async def on_get(self, req, resp: falcon.asgi.Response, **kwargs):
        try:
            req.context.compress = False        
            resp.data = read_large_file()
        except Exception as e:
            print(e)


app = falcon.asgi.App()
app.add_middleware(Middleware(compression_quality=0))
app.add_route("/default", NormalRoute())
app.add_route("/compress", CompressionRoute())