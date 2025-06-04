import pytest


@pytest.mark.parametrize("email, password, status_code, s_email, s_password, s_status_code", [
    ("koto_pes@test.com", "1234", 200, "Koto_pes@test.com", "234", 400),
    ("SpongeBob@test.com", "1234", 200, "spongebob@test.com", "234", 400),
])
async def test_users(ac, email, password, status_code, s_email, s_password, s_status_code):
    response = await ac.post(
        "auth/register",
        json={
            "email": email,
            "password": password
            }
    )
    assert response.status_code == status_code

    response = await ac.post(
        "auth/register",
        json={
            "email": s_email,
            "password": s_password
            }
    )
    assert response.status_code == s_status_code

    response = await ac.post(
        "auth/login",
        json={
            "email": email,
            "password": password
            }
    )
    access_cookie = response.cookies["access_token"]
    assert access_cookie
    assert ac.cookies["access_token"]
    assert response.status_code == 200

    response = await ac.get(
        "/auth/me"
    )
    assert response.status_code == 200
    res = response.json()
    assert res['email'] == email

    response = await ac.post(
        "/auth/logout"
    )
    assert response.status_code == 200
    assert "access_token" not in ac.cookies

    response = await ac.get(
        "/auth/me"
    )
    assert response.status_code == 401