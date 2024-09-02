import os
import json
import falcon
from casbin import Enforcer
from casbin.core_enforcer import EnforceContext
from casbin.persist.adapter import Adapter, load_policy_line
from casbin.persist.adapters import FileAdapter
from .user import User


class CustomFileAdapter(FileAdapter):

    def __init__(self, file_path):
        self._file_path: str = file_path

    def load_policy(self, model):
        if self._file_path.endswith(".json"):
            return self.load_policy_json(model)
        else:
            return super().load_policy(model)

    def load_policy_json(self, model):
        data = []
        with open(self._file_path, "rb") as file:
            data = json.loads(file.read())

        for item in data:
            tokens = []
            ptype = "g" if item["type"] == "group" else "p"

            if ptype == "p":
                tokens.append(ptype)
                tokens.append(item["sub"])
                if item.get("dom"):
                    tokens.append(item["dom"])
                tokens.append(item["obj"])
                tokens.append(item["act"])
            elif ptype == "g":
                tokens.append(ptype)
                tokens.append(item["sub"])
                tokens.append(item["grp"])
                if item.get("dom"):
                    tokens.append(item["dom"])
            load_policy_line(", ".join(tokens), model)


enforcer: Enforcer = None


def init():
    global enforcer

    MODEL_CONF_PATH = os.environ.get("CASBIN__MODEL_CONF_PATH")
    POLICY_PATH = os.environ.get("CASBIN__POLICY_PATH")

    enforcer = Enforcer(MODEL_CONF_PATH, CustomFileAdapter(POLICY_PATH), enable_log=True)


def authorize(obj: str = None, act: str = None):
    global enforcer

    def wrapped_hook(req: "falcon.Request", resp: "falcon.Response", *args):
        # https://falcon.readthedocs.io/en/stable/api/request_and_response_wsgi.html#id1
        user: User = req.context.user

        _obj = obj
        _act = act
        _dom = user.domain

        if _obj is None:
            _obj = req.path

        if _act is None:
            _act = req.method

        if _dom is None:
            _dom = req.host

        if not enforcer.enforce(user.ref, _dom, _obj, _act):
            resp.status = falcon.HTTP_403
            resp.complete = True

    return wrapped_hook
