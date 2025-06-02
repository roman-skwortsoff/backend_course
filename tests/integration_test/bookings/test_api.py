import pytest


@pytest.mark.parametrize("room_id, date_from, date_to, status_code", [
    (1, "2025-06-01", "2025-06-10", 200),
    (1, "2025-06-02", "2025-06-08", 200),
    (1, "2025-06-01", "2025-06-07", 200),
    (1, "2025-06-02", "2025-06-07", 200),
    (1, "2025-06-01", "2025-06-09", 200),
    (1, "2025-06-01", "2025-06-09", 409),
    (1, "2025-06-01", "2025-06-02", 200),
    (1, "2025-06-08", "2025-06-09", 200),
])
async def test_add_booking(
        room_id, date_from, date_to, status_code,
        db, authenticated_ac):
    # room_id = (await db.rooms.get_all())[0].id
    response = await authenticated_ac.post(
        "/bookings",
        json={"room_id": room_id,
              "date_from": date_from,
              "date_to": date_to,
              }
    )
    assert status_code == response.status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "booking" in res