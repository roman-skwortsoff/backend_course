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
