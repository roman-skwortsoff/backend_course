


async def test_get_facitities(ac):
    response = await ac.get(
        "/facilities",
        params={}
    )
    assert response.status_code == 200


async def test_post_facitities(ac):
    response = await ac.post(
        "/facilities",
        json={"title": "Джакузи"}
    )
    assert response.status_code == 200