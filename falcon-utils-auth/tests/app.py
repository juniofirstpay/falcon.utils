import falcon

from src.falcon_utils.auth import authorization
from src.falcon_utils.auth import user


authorization.init()

app = falcon.App()


def add_user(req, resp, *args, **kwargs):
    req.context.user = user.User(
        ref=req.headers.get("X-USER"), domain=req.headers.get("X-HOST")
    )


class ObjectRoute:

    @falcon.before(add_user)
    @falcon.before(authorization.authorize())
    def on_get(self, req, resp, *args, **kwargs):
        resp.media = {"status": "ok"}

class ObjectRoute2:

    @falcon.before(add_user)
    @falcon.before(authorization.authorize())
    def on_get(self, req, resp, *args, **kwargs):
        resp.media = {"status": "ok"}


app.add_route("/obj1", ObjectRoute())
app.add_route("/obj1/obj2", ObjectRoute2())
