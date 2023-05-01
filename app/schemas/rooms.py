from pydantic import BaseModel, Field, ConfigDict


class RoomAdd(BaseModel):
    title: str
    description: str | None = Field(None)
    price: int
    quantity: int

class RoomAddData(RoomAdd):
    hotel_id: int

class Room(RoomAdd):
    id: int
    hotel_id: int

    model_config = ConfigDict(from_attributes=True)


class RoomPATCH(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)

class RoomPatchData(RoomPATCH):
    hotel_id: int