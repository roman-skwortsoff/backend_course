from datetime import date

from app.schemas.bookings import BookingAddData


async def test_booking_crud(db):
    user_id = (await db.users.get_all())[0].id
    room_id = (await db.rooms.get_all())[0].id
    booking_data = BookingAddData(
        user_id=user_id,
        price=10000,
        date_from=date(year=2025, month=5, day=25),
        date_to=date(year=2025, month=5, day=27),
        room_id=room_id,
    )
    booking_data_add = await db.bookings.add(booking_data)
    await db.commit()

    booking_data_read = await db.bookings.get_one_or_none(
        room_id=room_id,
        user_id=user_id,
        date_from=booking_data_add.date_from,
        date_to=booking_data_add.date_to,
    )
    assert booking_data_read
    assert booking_data_read == booking_data_add

    update_booking = booking_data_read
    new_date_to = date(year=2025, month=6, day=1)
    update_booking.date_to = new_date_to
    booking_id = update_booking.id

    await db.bookings.edit(update_booking, id=booking_id)
    await db.commit()  # коммит только для фиксирования изменений, тест не будет падать без коммитов, т.к. весь тест внутри одной транзакции.

    new_update_booking = await db.bookings.get_one_or_none(id=booking_id)

    assert new_update_booking.date_to == new_date_to
    assert new_update_booking == update_booking

    await db.bookings.delete(id=booking_id)
    await db.commit()  # коммит только для фиксирования изменений, тест не будет падать без коммитов, т.к. весь тест внутри одной транзакции.

    res = await db.bookings.get_one_or_none(id=booking_id)

    assert res is None
    assert res != new_update_booking
