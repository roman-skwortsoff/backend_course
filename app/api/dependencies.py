from typing import Annotated
from fastapi import Depends, Query, Request
from pydantic import BaseModel
from elasticsearch import AsyncElasticsearch
from typing import AsyncGenerator

from app.database import async_session_maker
from app.exceptions import NotTokenException, NotTokenHTTPException
from app.services.auth import AuthService
from app.utils.db_manager import DB_Manager
from app.setup import mongo_manager, elasticsearch_manager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token", None)
    if access_token is None:
        raise NotTokenHTTPException
    return access_token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    try:
        data = AuthService().decode_token(token)
    except NotTokenException:
        raise NotTokenHTTPException
    return data["user_id"]


UserIdDep = Annotated[id, Depends(get_current_user_id)]


def get_db_manager():
    return DB_Manager(session_factory=async_session_maker)


async def get_db():
    async with (
        get_db_manager() as db
    ):  # можно async with DB_Manager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DB_Manager, Depends(get_db)]