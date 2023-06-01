async def test_get_me(authenticated_ac):
    response = await authenticated_ac.get(
        "/auth/me",
        params={}
    )
    assert response.status_code == 200