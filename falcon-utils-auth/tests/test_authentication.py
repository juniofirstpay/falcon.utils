import falcon.testing


def test_authentication():
    from .app import app

    # response = falcon.testing.simulate_get(
    #     app,
    #     "/obj1",
    #     headers={"X-API-KEY": "api-key-value", "Host": "app1.junio.in"},
    # )
    # assert response.status_code == 200

    # response = falcon.testing.simulate_get(
    #     app,
    #     "/obj1/obj2",
    #     headers={"Host": "app.junio.in"},
    # )
    # assert response.status_code == 401

    response = falcon.testing.simulate_get(
        app,
        "/obj/onlyauth",
        headers={"Host": "app.junio.in", "x-jwt": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImtGS0dpVlBiWm1xTmhBbEZrU1RwQ1RYYXFySUlKSzFnQ09iOGpjbzNEQ28ifQ.eyJkZXBlbmRhbnRzIjpbXSwiZXhwIjoxNzI1OTY5MjMyLCJncm91cHMiOlsiYWI1ZjNhNDctOWY4OS00ZWEzLTk5YjItMDhkOTIxYWU1ZmE1Il0sImlhdCI6MTcyNTk2NzQzMiwibW9iaWxlX251bWJlciI6Ijg0MzA4MzMwMzAiLCJuYW1lIjoiUHJha2hhciIsInBlcnNvbl9pZCI6ImFiNWYzYTQ3LTlmODktNGVhMy05OWIyLTA4ZDkyMWFlNWZhNSIsInByaXZpbGVnZXMiOlsiSU5ESVZJRFVBTCJdLCJwcm9maWxlcyI6eyJkZXBlbmRhbnRzIjpbXSwic2VsZiI6WyJhYjVmM2E0Ny05Zjg5LTRlYTMtOTliMi0wOGQ5MjFhZTVmYTUiXX0sInJvbGVzIjpbInVzZXIiXSwidXNlcl9pZCI6Ijk1YmJhMGU4LTVlMjItNGQ0My0xN2ZhLTA4ZDkyMWFlNWZhNiJ9.T4HY3LpMs1mikBzwOO3h1Tp9k2iBmGAAUJxFy8cKqvjt6ECibtgCV2swjyS2IwaunrtEGNrMpG8Q-WmpXOw1TJXBrEW0PWoQdSWdXys5WsO6IuXREzENr2kHd9rcUb2TmF4EBEvokqc0l34n8Z3GnsRN5UGIjHa0HR1LUOEkcgQ"},
    )
    assert response.status_code == 200

    # response = falcon.testing.simulate_get(
    #     app, "/obj1/obj2", headers={"Host": "root1.junio.in"}
    # )
    # assert response.status_code == 200

