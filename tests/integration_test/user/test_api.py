async def test_get_me(autenticated_ac):
    responce = await autenticated_ac.get(
        "/auth/me",
        params={}
    )
    assert responce.status_code == 200