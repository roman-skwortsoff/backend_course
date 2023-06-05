import pytest


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("koto_pes@test.com", "1234", 200),
        ("Koto_pes@test.com", "124", 400),
        ("SpongeBob@test.com", "1234", 200),
        ("bob@test", "1234", 422),
    ],
)
async def test_users(ac, email, password, status_code):
    # /register
    response = await ac.post(
        "auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == status_code

    if response.status_code != 200:
        return

    # /login
    response = await ac.post("auth/login", json={"email": email, "password": password})
    access_cookie = response.cookies["access_token"]
    assert access_cookie
    assert ac.cookies["access_token"]
    assert response.status_code == 200

    # /me
    response = await ac.get("/auth/me")
    assert response.status_code == 200
    res = response.json()
    assert res["email"] == email
    assert "password" not in res
    assert "hashed_password" not in res
    assert "id" in res

    # /logout
    response = await ac.post("/auth/logout")
    assert response.status_code == 200
    assert "access_token" not in ac.cookies

    # /me
    response = await ac.get("/auth/me")
    assert response.status_code == 401
