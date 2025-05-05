from datetime import date
from pydantic import BaseModel, Field, ConfigDict


class BookingAdd(BaseModel):
    date_from: date
    date_to: date
    room_id: int

class BookingAddData(BookingAdd):
    user_id: int
    price: int

class Booking(BookingAddData):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BookingPatch(BaseModel):
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)
    room_id: int | None = Field(None)

class BookingPatchData(BookingPatch):
    user_id: int
    price: int