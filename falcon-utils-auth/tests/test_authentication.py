import falcon.testing


def test_authentication():
    from .app import app

    response = falcon.testing.simulate_get(
        app,
        "/obj1",
        headers={"X-API-KEY": "api-key-value", "Host": "app1.junio.in"},
    )
    assert response.status_code == 200

    response = falcon.testing.simulate_get(
        app,
        "/obj1/obj2",
        headers={"Host": "app.junio.in"},
    )
    assert response.status_code == 401

    # response = falcon.testing.simulate_get(
    #     app, "/obj1/obj2", headers={"Host": "root1.junio.in"}
    # )
    # assert response.status_code == 200

