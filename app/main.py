# ruff: noqa: E402
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn
import logging
import sys
from pathlib import Path
from fastapi_cache import FastAPICache

# from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.DEBUG)

# from app.config import settings
from app.api import hotels, logs, rooms, bookings, facilities, images
from app.api import auth
from app.setup import redis_manager, mongo_manager
from app.api.dependencies import get_db
from app.middleware.logging import logging_middleware
from starlette.middleware.base import BaseHTTPMiddleware


async def regular_func():
    async for db in get_db():
        bookings = await db.bookings.get_booking_with_today_checkin()
        print(f"{bookings}")


async def regular_func_loop():
    while True:
        await regular_func()
        await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(regular_func_loop())
    await redis_manager.connect()
    await mongo_manager.connect()
    app.state.mongo_db = mongo_manager._db
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("Application started")
    yield
    await redis_manager.close()
    await mongo_manager.close()
    logging.info("Application shutdown")


# if settings.MODE == "TEST": #
#     FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


app = FastAPI(docs_url=None, lifespan=lifespan)

app.add_middleware(BaseHTTPMiddleware, dispatch=logging_middleware)


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


app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(hotels.router)
app.include_router(facilities.router)
app.include_router(bookings.router)
app.include_router(images.router)
app.include_router(logs.router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
