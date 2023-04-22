from fastapi import Query, APIRouter, Body, Path, HTTPException
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from app.api.dependencies import PaginationDep
from app.database import async_session_maker, engine
from app.models.hotels import HotelOrm
from app.schemas.hotels import Hotel

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
        filter_title: str | None = Query(None, description="Поиск по слову в названии"),
        filter_location: str | None = Query(None, description="Поиск по слову в адресе"),
):
    per_page = pagination.per_page or 5
    async with (async_session_maker() as session):
        query = select(HotelOrm)
        if filter_title:
            query = query.where(HotelOrm.title
                                .ilike(f"%{filter_title}%")
                                )
        if filter_location:
            query = query.where(HotelOrm.location
                                .ilike(f"%{filter_location}%"))
        query = (query
                 .limit(per_page)
                 .offset(per_page * (pagination.page - 1))
        )
        result = await session.execute(query)
        #print(type(result), result)
        hotels = result.scalars().all()
        return hotels


    # if pagination.per_page is not None:
    #     if pagination.page is None:
    #         pagination.page = 1
    #     end_index = pagination.page * pagination.per_page
    #     start_index = end_index - pagination.per_page
    #
    #     end_index = min(end_index, len(hotels_))
    #
    #     if start_index >= len(hotels_):
    #         max_pages = len(hotels_) // pagination.per_page + (1 if len(hotels_) % pagination.per_page != 0 else 0)
    #         raise HTTPException(
    #             status_code=400,
    #             detail=f"Страницы {pagination.page} не существует. Всего страниц : {max_pages}")
    #
    #     return hotels_[start_index: end_index]

    return hotels_


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
        add_hotel_stmt = insert(HotelOrm).values(**hotel_data.model_dump())
        print(add_hotel_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        await session.execute(add_hotel_stmt)
        await session.commit()
    return {"status": "OK"}


@router.put("/{hotel_id}")
def put_hotel(hotel_id: int = Path(..., description="Айдишник", gt=0),
              title: str = Body(..., description="Название"),
              name: str = Body(..., description="Имя")):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = title
            hotel["name"] = name
            return {"status": "OK"}
    raise HTTPException(status_code=404, detail="Неверный ID")


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
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}