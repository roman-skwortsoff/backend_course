


async def test_get_facitities(ac):
    responce = await ac.get(
        "/facilities",
        params={}
    )
    assert responce.status_code == 200


async def test_post_facitities(ac):
    responce = await ac.post(
        "/facilities",
        json={"title": "Джакузи"}
    )
    assert responce.status_code == 200