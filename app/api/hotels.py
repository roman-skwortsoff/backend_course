from fastapi import Query, APIRouter, Body, Path, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.api.dependencies import PaginationDep
from app.database import async_session_maker, engine
from app.models.hotels import HotelOrm
from app.schemas.hotels import Hotel
from repositories.hotels import HotelRepository

router = APIRouter(prefix="/hotels", tags=["Отели"])

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "dubai"},
    {"id": 3, "title": "Мальдивы", "name": "maldivi"},
    {"id": 4, "title": "Геленджик", "name": "gelendzhik"},
    {"id": 5, "title": "Москва", "name": "moscow"},
    {"id": 6, "title": "Казань", "name": "kazan"},
    {"id": 7, "title": "Санкт-Петербург", "name": "spb"},
]


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
        await HotelRepository(session).edit(id=hotel_id, data=hotel_data)
        await session.commit()
    return None



@router.patch("/{hotel_id}",
           summary="Частичное обновление данных об отеле",
           description="Тут мы частично обновляем данные, можно отправить name или title"
           )
def patch_hotel(hotel_id: int = Path(..., description="Айдишник", gt=0),
              title: str | None = Body(None, description="Название"),
              name: str | None = Body(None, description="Имя")):
    if title is None and name is None:
        raise HTTPException(status_code=400, detail="Не переданы значения")
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            if title:
                hotel["title"] = title
            if name:
                hotel["name"] = name
            return {"status": "OK"}
    raise HTTPException(status_code=404, detail="Неверный ID")


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int) -> None:
    async with async_session_maker() as session:
        await HotelRepository(session).delete(id=hotel_id)
        await session.commit()
    return None