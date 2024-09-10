import falcon.testing
from .app import app


def test_compression():
    resp = falcon.testing.simulate_get(app, "/default")
    assert resp.status_code == 200

    print("Normal", resp.headers['content-length'], resp.headers.get('content-encoding'))

    resp = falcon.testing.simulate_get(app, "/compress")
    assert resp.status_code == 200

    print("Compressed", resp.headers['content-length'], resp.headers.get('content-encoding'))
