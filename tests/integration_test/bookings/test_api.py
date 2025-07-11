import pytest
from sqlalchemy import delete

from app.models import BookingsOrm
from tests.conftest import get_db_null


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2025-06-01", "2025-06-10", 200),
        (1, "2025-06-02", "2025-06-08", 200),
        (1, "2025-06-01", "2025-06-07", 200),
        (1, "2025-06-02", "2025-06-07", 200),
        (1, "2025-06-01", "2025-06-09", 200),
        (1, "2025-06-01", "2025-06-09", 409),
        (1, "2025-06-01", "2025-06-02", 200),
        (1, "2025-06-08", "2025-06-09", 200),
    ],
)
async def test_add_booking(
    room_id, date_from, date_to, status_code, db, authenticated_ac
):
    # room_id = (await db.rooms.get_all())[0].id
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert status_code == response.status_code
    if status_code == 200:
        res = response.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "booking" in res


@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null():
        await _db.session.execute(delete(BookingsOrm))
        await _db.commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, rooms_booked",
    [
        (1, "2025-06-01", "2025-06-02", 1),
        (1, "2025-06-01", "2025-06-02", 2),
        (1, "2025-06-01", "2025-06-02", 3),
    ],
)
async def test_add_and_get_my_bookings(
    room_id, date_from, date_to, rooms_booked, delete_all_bookings, authenticated_ac
):
    response = await authenticated_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == 200

    response = await authenticated_ac.get("/bookings/me")
    data = response.json()
    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) == rooms_booked
