import json
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()


import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, insert
from wheel.metadata import yield_lines

from app.api.dependencies import get_db
from app.config import settings
from app.database import Base, engine_null, async_session_maker_null
from app.main import app
from app.models import *
from app.schemas.hotels import HotelAdd
from app.schemas.rooms import RoomAdd, RoomAddData
from app.setup import redis_manager
from app.utils.db_manager import DB_Manager


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"
    async with engine_null.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS citext'))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open('tests/mock_hotels.json', encoding="utf-8") as file_hotels:
        hotels_json = json.load(file_hotels)
    with open('tests/mock_rooms.json', encoding="utf-8") as file_rooms:
        rooms_json = json.load(file_rooms)

    hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_json]
    # rooms = [RoomAddData.model_validate(room) for room in rooms_json]

    async with DB_Manager(session_factory=async_session_maker_null) as db:
        await db.hotels.add_bulk(hotels)
        # await db.rooms.add_bulk(rooms) # можно и так сделать удалив сырой sql запрос
        stmt = insert(RoomsOrm).values(rooms_json)
        await db.session.execute(stmt)
        await db.commit()


async def get_db_null():
    await redis_manager.connect()
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        yield db
    await redis_manager.close()

app.dependency_overrides[get_db] = get_db_null

# для запуска в lifespan
# @pytest.fixture(scope="function")
# async def ac() -> AsyncClient:
#     async with app.router.lifespan_context(app):
#         async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
#             yield ac

@pytest.fixture(scope="function")
async def ac() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="function")
async def db() -> DB_Manager:
    async with DB_Manager(session_factory=async_session_maker_null) as db:
        yield db


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "auth/register",
            json={
                "email": "kot@pes.ru",
                "password": "1234"
                }
            )