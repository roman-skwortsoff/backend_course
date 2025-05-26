from datetime import date

from app.schemas.bookings import BookingAddData



async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAddData(
        user_id = user_id,
        price = 10000,
        date_from = date(year=2025, month=5, day=25),
        date_to = date(year=2025, month=5, day=27),
        room_id = room_id,
    )
    booking_data_add = await db.bookings.add(booking_data)
    await db.commit()






