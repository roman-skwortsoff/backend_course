from fastapi import Query, APIRouter, Body, Path, HTTPException
from dependencies import PaginationDep

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


@router.get("", summary="Показываем список отелей, по умолчанию по 5 на странице",)
def get_hotels(
        pagination: PaginationDep,
        id: int | None = Query(None, description="Айдишник"),
        title: str | None = Query(None, description="Название отеля"),
):
    hotels_ = []

    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)

    if pagination.per_page is not None:
        if pagination.page is None:
            pagination.page = 1
        end_index = pagination.page * pagination.per_page
        start_index = end_index - pagination.per_page

        end_index = min(end_index, len(hotels_))

        if start_index >= len(hotels_):
            max_pages = len(hotels_) // pagination.per_page + (1 if len(hotels_) % pagination.per_page != 0 else 0)
            raise HTTPException(
                status_code=400,
                detail=f"Страницы {pagination.page} не существует. Всего страниц : {max_pages}")

        return hotels_[start_index: end_index]

    return hotels_


@router.post("")
def create_hotel(title: str = Body(..., description="Название"),
                 name: str = Body(..., description="Имя")
                 ):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": title,
        "name": name
    })
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