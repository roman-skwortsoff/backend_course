from pydantic import BaseModel, Field, ConfigDict


class RoomAdd(BaseModel):
    title: str
    description: str | None = Field(None)
    price: int
    quantity: int
    facilities_ids: list[int] | None = None

class RoomAddData(BaseModel):
    hotel_id: int
    title: str
    description: str | None = Field(None)
    price: int
    quantity: int

class Room(RoomAddData):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RoomPATCH(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)
    facilities_ids: list[int] | None = Field()

class RoomPatchData(BaseModel):
    hotel_id: int
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)