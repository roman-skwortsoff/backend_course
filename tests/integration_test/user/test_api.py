async def test_get_me(autenticated_ac):
    response = await autenticated_ac.get(
        "/auth/me",
        params={}
    )
    assert response.status_code == 200