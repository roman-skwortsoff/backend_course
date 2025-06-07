from datetime import date
from fastapi import HTTPException

from fastapi import Query, APIRouter, Body
from app.api.dependencies import PaginationDep, DBDep
from app.exceptions import (
    IncorrectDatesException,
    ObjectNotFoundException,
    DataBaseIntegrityException,
)
from app.schemas.facilities import RoomFacilityAdd
from app.schemas.rooms import RoomAdd, RoomPATCH, RoomAddData, RoomPatchData

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
    per_page = pagination.per_page or 5
    return await db.rooms.get_all_rooms_in_hotels(
        description=description,
        title=title,
        limit=per_page or 5,
        offset=per_page * (pagination.page - 1),
    )


@router.get("/{hotel_id}/rooms", summary="Показываем список номеров в отеле")
async def get_rooms(
    hotel_id: int,
    db: DBDep,
    date_from: date = Query(example="2025-05-07", description="Дата приезда"),
    date_to: date = Query(example="2025-05-08", description="Дата отъезда"),
):
    try:
        return await db.rooms.get_filtered_by_date(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
    except IncorrectDatesException as ex:
        raise HTTPException(status_code=400, detail=ex.detail)


@router.get("/{hotel_id}/rooms/{room_id}", summary="Показываем определенный номер")
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    try:
        return await db.rooms.get_one(hotel_id=hotel_id, id=room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=404, detail="Данного номера не существует")


@router.post("/{hotel_id}/rooms")
async def create_room(
    hotel_id: int, db: DBDep, room_data: RoomAdd = Body(openapi_examples={})
):
    merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
    try:
        room = await db.rooms.add(merged_data)
    except DataBaseIntegrityException:
        raise HTTPException(status_code=400, detail="Неверно указан отель")
    room_facilities_data = [
        RoomFacilityAdd(room_id=room.id, facility_id=f_id)
        for f_id in room_data.facilities_ids
    ]
    await db.rooms_facilities.add_bulk(room_facilities_data)
    await db.commit()
    return {"status": "OK", "room": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def put_room(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomAdd = Body()
) -> None:
    merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
    try:
        await db.rooms.edit(merged_data, id=room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=400, detail="Указан несуществующий номер")
    await db.rooms_facilities.set_facilities_by_room(
        room_id=room_id, facility_ids=room_data.facilities_ids
    )
    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}/rooms/{room_id}",
    summary="Частичное обновление данных о номерах",
    description="Тут мы частично обновляем данные, можно отправить любое из полей",
)
async def patch_room(
    hotel_id: int, room_id: int, db: DBDep, room_data: RoomPATCH = Body()
):
    room_data_dict = room_data.model_dump(exclude_unset=True)
    merged_data = RoomPatchData(**room_data_dict, hotel_id=hotel_id)
    try:
        await db.rooms.edit(merged_data, is_patch=True, id=room_id)
    except ObjectNotFoundException:
        raise HTTPException(status_code=400, detail="Указан несуществующий номер")

    if "facilities_ids" in room_data_dict:
        await db.rooms_facilities.set_facilities_by_room(
            room_id=room_id, facility_ids=room_data_dict["facilities_ids"]
        )

    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep) -> None:
    try:
        await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=400, detail="Нельзя удалить несуществующий номер"
        )
    except DataBaseIntegrityException:
        raise HTTPException(
            status_code=409, detail="Нужно сначала удалить взаимосвязанные данные"
        )
    await db.commit()
    return {"status": "OK"}
