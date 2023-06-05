async def test_get_hotels(ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2023-05-27",
            "date_to": "2023-05-28",
        },
    )
    assert response.status_code == 200
