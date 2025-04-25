from fastapi import Query, APIRouter, Body, Path, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.api.dependencies import PaginationDep
from app.database import async_session_maker, engine
from app.models.hotels import HotelOrm
from app.schemas.hotels import Hotel, HotelPATCH
from repositories.hotels import HotelRepository

router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get("", summary="Показываем список отелей, изначально по 5 на странице",)
async def get_hotels(
        pagination: PaginationDep,
        location: str | None = Query(None, description="Локация"),
        title: str | None = Query(None, description="Название отеля"),
):

    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelRepository(session).get_all(
            location=location,
            title=title,
            limit=per_page or 5,
            offset=per_page*(pagination.page-1)
        )


@router.post("")
async def create_hotel(hotel_data: Hotel = Body(openapi_examples={
    "1": {
         "summary": "Сочи",
         "value": {
             "title": "Отель Сочи 5 звезд у моря",
             "location": "ул. Моря, 1",
         }
    }
}
)):
    async with async_session_maker() as session:
        hotel = await HotelRepository(session).add(hotel_data)
        await session.commit()
    return {"status": "OK", "hotel": hotel}


@router.put("/{hotel_id}")
async def put_hotel(hotel_id: int, hotel_data: Hotel = Body()) -> None:
    async with async_session_maker() as session:
        await HotelRepository(session).edit(hotel_data, id=hotel_id)
        await session.commit()
    return {"status": "OK"}



@router.patch("/{hotel_id}",
           summary="Частичное обновление данных об отеле",
           description="Тут мы частично обновляем данные, можно отправить name или title"
           )
async def patch_hotel(hotel_id: int, hotel_data: HotelPATCH
              ):
    async with async_session_maker() as session:
        await HotelRepository(session).edit(hotel_data, is_patch=True, id=hotel_id)
        await session.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int) -> None:
    async with async_session_maker() as session:
        await HotelRepository(session).delete(id=hotel_id)
        await session.commit()
    return {"status": "OK"}

@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int):
    async with async_session_maker() as session:
        hotel = await HotelRepository(session).get_one_or_none(id = hotel_id)
        await session.commit()
    return hotel