from fastapi import Query, APIRouter, Body
from app.api.dependencies import PaginationDep, DBDep, UserIdDep
from app.repositories.rooms import RoomsRepository
from app.schemas.bookings import BookingAdd, BookingPatch, BookingAddData, BookingPatchData

router = APIRouter(prefix="/bookings", tags=["Бронирования"])


@router.post("")
async def create_booking(db: DBDep,
                         user_id: UserIdDep,
                         booking_data: BookingAdd = Body(openapi_examples={})
                         ):
    room = await db.rooms.get_one_or_none(id=booking_data.room_id)
    merged_data = BookingAddData(**booking_data.model_dump(), price=room.price, user_id=user_id)
    booking = await db.bookings.add(merged_data)
    await db.commit()
    return {"status": "OK", "booking": booking}

@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user_id: UserIdDep, db: DBDep) -> None:
    await db.bookings.delete(id=booking_id, user_id=user_id)
    await db.commit()
    return {"status": "OK"}