from datetime import date

from fastapi import Query, APIRouter, Body
from app.api.dependencies import PaginationDep, DBDep
from app.schemas.facilities import RoomFacilityAdd
from app.schemas.rooms import RoomAdd, Room, RoomPATCH, RoomAddData, RoomPatchData

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/rooms", summary="Весь список номеров во всех отелях, изначально по 5 на странице")
async def get_all_rooms(
        pagination: PaginationDep,
        db: DBDep,
        description: str | None = Query(None, description="Описание"),
        title: str | None = Query(None, description="Название номера"),
        ):
    per_page = pagination.per_page or 5
    return await db.rooms.get_all(
        description=description,
        title=title,
        limit=per_page or 5,
        offset=per_page * (pagination.page - 1)
    )

@router.get("/{hotel_id}/rooms", summary="Показываем список номеров в отеле")
async def get_rooms(hotel_id: int,
                    db: DBDep,
                    date_from: date = Query(example='2025-05-07', description="Дата приезда"),
                    date_to: date = Query(example='2025-05-08', description="Дата отъезда")
                    ):
    return await db.rooms.get_filtered_by_date(hotel_id=hotel_id, date_from=date_from, date_to=date_to)

@router.get("/{hotel_id}/rooms/{room_id}", summary="Показываем определенный номер")
async def get_room(hotel_id: int, room_id: int, db: DBDep):
    return await db.rooms.get_one_or_none(hotel_id=hotel_id, id=room_id)


@router.post("/{hotel_id}/rooms")
async def create_room(hotel_id: int, db: DBDep, room_data: RoomAdd = Body(openapi_examples={})):
    merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
    room = await db.rooms.add(merged_data)
    room_facilities_data = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids]
    await db.rooms_facilities.add_bulk(room_facilities_data)
    await db.commit()
    return {"status": "OK", "room": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def put_room(hotel_id: int,
                   room_id: int,
                   db: DBDep,
                   room_data: RoomAdd = Body()
                   ) -> None:
    merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
    await db.rooms.edit(merged_data, id=room_id)

    facilities = await db.rooms_facilities.get_filtered(room_id=room_id)
    facility_ids = {facility.facility_id for facility in facilities}
    new_facility_ids = set(room_data.facilities_ids)

    to_remove = facility_ids - new_facility_ids
    to_add = new_facility_ids - facility_ids

    if to_remove:
        await db.rooms_facilities.delete_by_room_and_facilities(room_id=room_id, facility_ids=list(to_remove))

    if to_add:
        room_facilities_data = [RoomFacilityAdd(room_id=room_id, facility_id=f_id) for f_id in to_add]
        await db.rooms_facilities.add_bulk(room_facilities_data)

    await db.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}",
           summary="Частичное обновление данных о номерах",
           description="Тут мы частично обновляем данные, можно отправить любое из полей"
           )
async def patch_room(hotel_id: int,
                     room_id: int,
                     db: DBDep,
                     room_data: RoomPATCH = Body()
              ):
    merged_data = RoomPatchData(**room_data.model_dump(exclude_unset=True), hotel_id=hotel_id)
    await db.rooms.edit(merged_data, is_patch=True, id=room_id)

    if "facilities_ids" in room_data:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!")
        facilities = await db.rooms_facilities.get_filtered(room_id=room_id)
        facility_ids = {facility.facility_id for facility in facilities}
        new_facility_ids = set(room_data.facilities_ids)

        to_remove = facility_ids - new_facility_ids
        to_add = new_facility_ids - facility_ids

        if to_remove:
            await db.rooms_facilities.delete_by_room_and_facilities(room_id=room_id, facility_ids=list(to_remove))

        if to_add:
            room_facilities_data = [RoomFacilityAdd(room_id=room_id, facility_id=f_id) for f_id in to_add]
            await db.rooms_facilities.add_bulk(room_facilities_data)

    await db.commit()
    return {"status": "OK"}

@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(hotel_id: int, room_id: int, db: DBDep) -> None:
    await db.rooms.delete(id=room_id, hotel_id=hotel_id)
    await db.commit()
    return {"status": "OK"}



#
# @router.patch("/{hotel_id}",
#            summary="Частичное обновление данных об отеле",
#            description="Тут мы частично обновляем данные, можно отправить name или title"
#            )
# async def patch_hotel(hotel_id: int, hotel_data: HotelPATCH
#               ):
#     async with async_session_maker() as session:
#         await HotelRepository(session).edit(hotel_data, is_patch=True, id=hotel_id)
#         await session.commit()
#     return {"status": "OK"}
#
#
# @router.delete("/{hotel_id}")
# async def delete_hotel(hotel_id: int) -> None:
#     async with async_session_maker() as session:
#         await HotelRepository(session).delete(id=hotel_id)
#         await session.commit()
#     return {"status": "OK"}
#
# @router.get("/{hotel_id}")
# async def get_hotel(hotel_id: int):
#     async with async_session_maker() as session:
#         hotel = await HotelRepository(session).get_one_or_none(id = hotel_id)
#         await session.commit()
#     return hotel