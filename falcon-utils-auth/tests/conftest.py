import os
import json
import pytest

MODEL_CONF = """
[request_definition]
r = sub, dom, obj, act

[policy_definition]
p = sub, dom, obj, act

[role_definition]
g = _, _, _
g2 = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = (((g(r.sub, p.sub, r.dom) && r.dom == p.dom) || (r.sub == p.sub &&(r.dom == p.dom || p.dom == '*'))) && keyMatch(r.obj, p.obj) && r.act == p.act) || (g('*', p.sub, r.dom) && keyMatch(r.obj, p.obj) && r.act == p.act)
"""

POLICY = [
    {
        "type": "policy",
        "sub": "admin",
        "obj": "/obj1",
        "dom": "vouchers.junio.in",
        "act": "GET",
    },
    {
        "type": "policy",
        "sub": "anonymous",
        "obj": "/obj1/obj2",
        "dom": "app.junio.in",
        "act": "GET",
    },
    {
        "type": "policy",
        "sub": "admin",
        "obj": "/obj1/*",
        "dom": "vouchers.junio.in",
        "act": "GET",
    },
    {
        "type": "policy",
        "sub": "admin",
        "obj": "/obj1/*",
        "dom": "app.junio.in",
        "act": "GET",
    },
    {
        "type": "policy",
        "sub": "user",
        "obj": "/obj1/*",
        "dom": "root.junio.in",
        "act": "GET",
    },
    {"type": "group", "sub": "user-1", "grp": "admin", "dom": "vouchers.junio.in"},
    {"type": "group", "sub": "user-2", "grp": "admin", "dom": "*"},
    {"type": "group", "sub": "*", "grp": "admin", "dom": "app1.junio.in"},
]


@pytest.fixture(scope="session", autouse=True)
def configure_files():
    with open("/tmp/casbin_model.conf", "w") as file:
        file.write(MODEL_CONF)

    with open("/tmp/casbin_policy.json", "w") as file:
        file.write(json.dumps(POLICY))

    os.environ["CASBIN__MODEL_CONF_PATH"] = "/tmp/casbin_model.conf"
    os.environ["CASBIN__POLICY_PATH"] = "/tmp/casbin_policy.json"

    yield

    os.remove(os.environ["CASBIN__MODEL_CONF_PATH"])
    os.remove(os.environ["CASBIN__POLICY_PATH"])
