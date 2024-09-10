import falcon

from src.falcon_utils.auth import Auth, AuthConfig

config_dict = {
    "schemes": [1, 2, 3, 4],
    "api_keys": {"api-key-value": "api-key-client"},
    "headers": {4: ["X-API-KEY"], 3: ["X-JWT"]},
    "authorization_model": "/tmp/casbin_model.conf",
    "authorization_policy": "/tmp/casbin_policy.json",
    "jwks": [
        "http://backend.junio.com/api/authorization/jwks",
        {
            "x-api-version": "v1"
        }
    ]
}


auth = Auth(AuthConfig(**config_dict))

app = falcon.App()
app.add_middleware(auth.middleware)


class ObjectRoute:

    @falcon.before(auth.authenticate())
    @falcon.before(auth.authorize())
    def on_get(self, req, resp, *args, **kwargs):
        resp.media = {"status": "ok"}


class ObjectRoute2:

    @falcon.before(auth.authenticate(auth=False))
    @falcon.before(auth.authorize())
    def on_get(self, req, resp, *args, **kwargs):
        resp.media = {"status": "ok"}


class ObjectRouteOnlyAuthenticate:
    
    @falcon.before(auth.authenticate(auth=True))
    def on_get(self, req, resp, *args, **kwargs):
        resp.media = {"status": "ok"}

app.add_route("/obj1", ObjectRoute())
app.add_route("/obj1/obj2", ObjectRoute2())
app.add_route("/obj/onlyauth", ObjectRouteOnlyAuthenticate())
