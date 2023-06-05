from datetime import date

from fastapi import Query, APIRouter, Body
from fastapi_cache.decorator import cache

from app.api.dependencies import PaginationDep, DBDep
from app.schemas.hotels import HotelAdd, HotelPATCH


router = APIRouter(prefix="/hotels", tags=["Отели"])


@router.get(
    "",
    summary="Показываем список отелей, изначально по 5 на странице",
)
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    date_from: date = Query(example="2025-05-07", description="Дата приезда"),
    date_to: date = Query(example="2025-05-08", description="Дата отъезда"),
    location: str | None = Query(None, description="Локация"),
    title: str | None = Query(None, description="Название отеля"),
):
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_date(
        date_from=date_from,
        date_to=date_to,
        location=location,
        title=title,
        limit=per_page or 5,
        offset=per_page * (pagination.page - 1),
    )


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {
                    "title": "Отель Сочи 5 звезд у моря",
                    "location": "ул. Моря, 1",
                },
            }
        }
    ),
):
    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "hotel": hotel}


@router.put("/{hotel_id}")
async def put_hotel(hotel_id: int, db: DBDep, hotel_data: HotelAdd = Body()) -> None:
    await db.hotels.edit(hotel_data, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="Тут мы частично обновляем данные, можно отправить name или title",
)
async def patch_hotel(hotel_id: int, db: DBDep, hotel_data: HotelPATCH):
    await db.hotels.edit(hotel_data, is_patch=True, id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep) -> None:
    await db.hotels.delete(id=hotel_id)
    await db.commit()
    return {"status": "OK"}


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    return hotel
