


async def test_get_hotels(ac):
    responce = await ac.get(
        "/hotels",
        params={
            "date_from": "2025-05-27",
            "date_to": "2025-05-28",
        }
    )
    assert responce.status_code == 200