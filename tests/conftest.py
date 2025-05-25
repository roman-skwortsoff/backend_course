import json

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine_null
from app.main import app
from app.models import *


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    assert settings.MODE == "TEST"
    async with engine_null.begin() as conn:
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS citext'))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


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


@pytest.fixture(scope="session", autouse=True)
async def register_hotels(setup_database):
    with open('tests/mock_hotels.json', 'r') as file:
        f = file.read()
    data = json.loads(f)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for item in data:
            await ac.post(
                "/hotels",
                json=item
            )


@pytest.fixture(scope="session", autouse=True)
async def register_rooms(register_hotels):
    with open('tests/mock_rooms.json', 'r') as file:
        data = json.loads(file.read())
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        for item in data:
            hotel_id = item.pop("hotel_id")
            await ac.post(
                f"/hotels/{hotel_id}/rooms",
                json=item
            )