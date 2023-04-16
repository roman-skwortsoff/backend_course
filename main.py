from fastapi import FastAPI, Query, Body, Path, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
from requests_toolbelt.multipart.encoder import total_len

app = FastAPI(docs_url=None)

@app.get("/")
def func():
    return "Hello World!"


hotels = [
    {"id": 1, "title": "Sochi", "name": "Сочи"},
    {"id": 2, "title": "Dubai", "name": "Дубай"},
]


@app.get("/hotels")
def get_hotels(
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
    return hotels_


@app.post("/hotels")
def create_hotel(
        title: str = Body(...),
        name: str = Body(...)
):
    global hotels
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": title,
        "name": name
    })
    return {"status": "OK"}

@app.put("/hotels/{hotel_id}")
def put_hotel(hotel_id: int = Path(..., description="Айдишник", gt=0),
              title: str = Body(..., description="Название"),
              name: str = Body(..., description="Имя")):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = title
            hotel["name"] = name
            return hotel
    raise HTTPException(status_code=404, detail="Неверный ID")

@app.patch("/hotels/{hotel_id}")
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
            return hotel
    raise HTTPException(status_code=404, detail="Неверный ID")




@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)