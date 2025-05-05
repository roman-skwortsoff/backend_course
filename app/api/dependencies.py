from typing import Annotated
from fastapi import Depends, Query, Request, HTTPException
from pydantic import BaseModel

from app.database import async_session_maker
from app.services.auth import AuthService
from app.utils.db_manager import DB_Manager


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, lt=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    access_token = request.cookies.get('access_token', None)
    if access_token is None:
        raise HTTPException(status_code=401, detail="Вы не предоставили токен")
    return access_token


def get_current_user_id(token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(token)
    return data['user_id']


UserIdDep = Annotated[id, Depends(get_current_user_id)]


def get_db_manager():
    return DB_Manager(session_factory=async_session_maker)


async def get_db():
    async with get_db_manager() as db: # можно async with DB_Manager(session_factory=async_session_maker) as db:
        yield db


DBDep = Annotated[DB_Manager, Depends(get_db)]