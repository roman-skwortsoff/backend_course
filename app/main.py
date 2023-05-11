from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.api import hotels, rooms, bookings, facilities
from app.api import auth
from app.core.exceptions import register_exceptions


app = FastAPI(docs_url=None)

@app.get("/")
def func():
    return "Hello World!"


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

register_exceptions(app)

app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(hotels.router)
app.include_router(facilities.router)
app.include_router(bookings.router)



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

