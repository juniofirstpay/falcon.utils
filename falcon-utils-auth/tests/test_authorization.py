import falcon.testing


def test_authorization():
    from .app import app

    response = falcon.testing.simulate_get(
        app, "/obj1/obj2", headers={"x-user": "user-1", "x-host": "root1.junio.in"}
    )
    response = falcon.testing.simulate_get(
        app, "/obj1/*", headers={"x-user": "user-1", "x-host": "root1.junio.in"}
    )

    assert response.status_code == 200
