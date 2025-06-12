from datetime import date

from fastapi import Query, APIRouter, Body
from fastapi_cache.decorator import cache

from app.api.dependencies import PaginationDep, DBDep
from app.exceptions import (
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
)
from app.schemas.hotels import HotelAdd, HotelPATCH
from app.services.hotels import HotelService

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
    hotels = await HotelService(db).get_filtered_by_time(
        pagination, date_from, date_to, location, title
    )
    return {"status": "OK", "data": hotels}


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
    hotel = await HotelService(db).create_hotel(hotel_data)
    return {"status": "OK", "hotel": hotel}


@router.put("/{hotel_id}")
async def put_hotel(hotel_id: int, db: DBDep, hotel_data: HotelAdd = Body()) -> None:
    try:
        await HotelService(db).put_hotel(hotel_id, hotel_data)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.patch(
    "/{hotel_id}",
    summary="Частичное обновление данных об отеле",
    description="Тут мы частично обновляем данные, можно отправить name или title",
)
async def patch_hotel(hotel_id: int, db: DBDep, hotel_data: HotelPATCH) -> None:
    try:
        await HotelService(db).patch_hotel(hotel_id, hotel_data)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int, db: DBDep) -> None:
    try:
        await HotelService(db).delete_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.get("/{hotel_id}")
async def get_hotel(hotel_id: int, db: DBDep):
    try:
        return await HotelService(db).get_hotel(hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
