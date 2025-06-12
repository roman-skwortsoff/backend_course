from datetime import date
from fastapi import HTTPException

from fastapi import Query, APIRouter, Body
from app.api.dependencies import PaginationDep, DBDep
from app.exceptions import (
    IncorrectDatesException,
    ObjectNotFoundException,
    DataBaseIntegrityException,
    HotelNotFoundHTTPException,
    RoomNotFoundHTTPException,
    HotelNotFoundException,
    RoomNotFoundException,
    DBIntegrityHTTPException,
)
from app.schemas.rooms import RoomAdd, RoomPATCH
from app.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get(
    "/rooms", summary="Весь список номеров во всех отелях, изначально по 5 на странице"
)
async def get_all_rooms(
    pagination: PaginationDep,
    db: DBDep,
    description: str | None = Query(None, description="Описание"),
    title: str | None = Query(None, description="Название номера"),
):
    return await RoomService(db).get_all_rooms(pagination, description, title)


@router.get("/{hotel_id}/rooms", summary="Показываем список номеров в отеле")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-05-07", description="Дата приезда"),
    date_to: date = Query(example="2025-05-08", description="Дата отъезда"),
):
    try:
        return await RoomService(db).get_rooms(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
    except IncorrectDatesException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)


@router.get("/{hotel_id}/rooms/{room_id}", summary="Показываем определенный номер")
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        return await RoomService(db).get_room(hotel_id, room_id)
    except ObjectNotFoundException:
        raise RoomNotFoundHTTPException


@router.post("/{hotel_id}/rooms")
async def create_room(
    hotel_id: int, db: DBDep, room_data: RoomAdd = Body(openapi_examples={})
):
    try:
        room = await RoomService(db).create_room(hotel_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK", "room": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def put_room(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomAdd = Body()
) -> None:
    try:
        await RoomService(db).put_room(hotel_id, room_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частичное обновление данных о номерах",
    description="Тут мы частично обновляем данные, можно отправить любое из полей",
)
async def patch_room(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomPATCH = Body()
):
    try:
        await RoomService(db).patch_room(hotel_id, room_id, room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep) -> None:
    try:
        await RoomService(db).delete_room(hotel_id, room_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except DataBaseIntegrityException:
        raise DBIntegrityHTTPException
    return {"status": "OK"}
