from fastapi import APIRouter, Body, HTTPException

from app.api.dependencies import DBDep, UserIdDep
from app.exceptions import (
    ObjectNotFoundException,
    AllRoomsAreBookedException,
    RoomNotFoundHTTPException,
)
from app.schemas.bookings import BookingAdd, BookingAddData

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.get("")
async def get_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me")
async def get_user_bookings(db: DBDep, user_id: UserIdDep):
    return await db.bookings.get_filtered(user_id=user_id)


@router.post("")
async def create_booking(
    db: DBDep, user_id: UserIdDep, booking_data: BookingAdd = Body(openapi_examples={})
):
    try:
        room = await db.rooms.get_one(id=booking_data.room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException  # HTTPException(status_code=400, detail="Номер не найден")  # Можно detail=ex.detail
    merged_data = BookingAddData(
        **booking_data.model_dump(), price=room.price, user_id=user_id
    )
    try:
        booking = await db.bookings.add_booking(merged_data, hotel_id=room.hotel_id)
    except AllRoomsAreBookedException as ex:
        raise HTTPException(status_code=409, detail=ex.detail)
    await db.commit()
    return {"status": "OK", "booking": booking}


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user_id: UserIdDep, db: DBDep) -> None:
    await db.bookings.delete(id=booking_id, user_id=user_id)
    await db.commit()
    return {"status": "OK"}
