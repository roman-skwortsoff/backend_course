from fastapi import Query, APIRouter, Body
from app.api.dependencies import PaginationDep
from app.database import async_session_maker
from app.repositories.hotels import HotelRepository
from app.repositories.rooms import RoomsRepository
from app.schemas.rooms import RoomAdd, Room, RoomPATCH, RoomAddData, RoomPatchData

router = APIRouter(prefix="/hotels", tags=["Номера"])


@router.get("/rooms", summary="Весь список номеров, изначально по 5 на странице")
async def get_all_rooms(
        pagination: PaginationDep,
        description: str | None = Query(None, description="Описание"),
        title: str | None = Query(None, description="Название номера"),
        ):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_all(
            description=description,
            title=title,
            limit=per_page or 5,
            offset=per_page * (pagination.page - 1)
        )

@router.get("/{hotel_id}/rooms", summary="Показываем список номеров в отеле",)
async def get_rooms(hotel_id: int):
    async with async_session_maker() as session:
        return await RoomsRepository(session).get_rooms_in_hotel(hotel_id)


@router.post("/{hotel_id}/rooms")
async def create_room(hotel_id: int, room_data: RoomAdd = Body(openapi_examples={})):
    merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
    async with async_session_maker() as session:
        room = await RoomsRepository(session).add(merged_data)
        await session.commit()
    return {"status": "OK", "room": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def put_room(hotel_id: int,
                   room_id: int,
                   room_data: RoomAdd = Body()
                   ) -> None:
    merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(merged_data, id=room_id)
        await session.commit()
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}",
           summary="Частичное обновление данных о номерах",
           description="Тут мы частично обновляем данные, можно отправить любое из полей"
           )
async def patch_room(hotel_id: int, room_id: int, room_data: RoomPATCH = Body()
              ):
    merged_data = RoomPatchData(**room_data.model_dump(exclude_unset=True), hotel_id=hotel_id)
    async with async_session_maker() as session:
        await RoomsRepository(session).edit(merged_data, is_patch=True, id=room_id)
        await session.commit()
    return {"status": "OK"}
#
#
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