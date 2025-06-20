from fastapi import APIRouter, Body
import json

from app.api.dependencies import DBDep, UserIdDep
from app.config import settings
from app.exceptions import (
    ObjectNotFoundException,
    AllRoomsAreBookedException,
    RoomNotFoundHTTPException, RoomNotFoundException, AllRoomsAreBookedHTTPException, ObjectNotFoundHTTPException,
)
from app.kafka.producer import send_message
from app.schemas.bookings import BookingAdd
from app.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Бронирования"])

@router.post("/send-kafka/")
def send_kafka(msg: str):
    send_message('test-topic', msg)
    return {"status": "sent", "msg": msg}

@router.get("")
async def get_bookings(db: DBDep):
    return await BookingService(db).get_bookings()


@router.get("/me")
async def get_user_bookings(db: DBDep, user_id: UserIdDep):
    return await BookingService(db).get_user_bookings(user_id=user_id)


@router.post("")
async def create_booking(
    db: DBDep, user_id: UserIdDep, booking_data: BookingAdd = Body(openapi_examples={})
):
    # try:
    #     booking = await BookingService(db).create_booking(user_id, booking_data)
    # except RoomNotFoundException:
    #     raise RoomNotFoundHTTPException
    # except AllRoomsAreBookedException:
    #     raise AllRoomsAreBookedHTTPException
    # return {"status": "OK", "booking": booking}
    message = {
        "user_id": user_id,
        "booking_data": booking_data.model_dump(mode="json")
    }
    print("!!!!!!!!!!", message)
    send_message("booking-topic", json.dumps(message))
    return {"status": "accepted", "detail": "Booking request sent to Kafka"}


@router.delete("/{booking_id}")
async def delete_booking(booking_id: int, user_id: UserIdDep, db: DBDep) -> None:
    try:
        await BookingService(db).delete_booking(booking_id, user_id)
    except ObjectNotFoundException:
        raise ObjectNotFoundHTTPException
    return {"status": "OK"}
