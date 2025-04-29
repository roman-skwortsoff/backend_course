import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from app.config import settings


engine = create_async_engine(settings.DB_URL, echo = True)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

session = async_session_maker()

class Base(DeclarativeBase):
    pass
