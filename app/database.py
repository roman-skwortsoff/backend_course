import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, NullPool

from app.config import settings

# альтернатива в тестах app.dependency_overrides[get_db] = get_db_null
db_params = {}
# if settings.MODE == "TEST":
#     db_params = {"poolclass": NullPool}


engine = create_async_engine(settings.DB_URL, echo = True, **db_params)
engine_null = create_async_engine(settings.DB_URL, echo=True, poolclass=NullPool)

async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)
async_session_maker_null = async_sessionmaker(bind=engine_null, expire_on_commit=False)

session = async_session_maker()

class Base(DeclarativeBase):
    pass
