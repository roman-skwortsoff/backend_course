from datetime import datetime, timezone, timedelta
from os import access

from fastapi import APIRouter, HTTPException, Response, Request

from app.config import settings
from app.database import async_session_maker
from app.repositories.users import UsersRepository
from app.schemas.users import UserRequestAdd, UserAdd
from app.services.auth import AuthService

router = APIRouter(prefix='/auth', tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(
        data: UserRequestAdd,
        response: Response
):
    # hashed_password = pwd_context.hash(data.password)
    # new_user_data = UserAdd(email=data.email, password=hashed_password)
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
        if not AuthService().verify_password(data.password, user.password):
            raise HTTPException(status_code=401, detail="Пароль неверный")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}


@router.post("/register")
async def register_user(data: UserRequestAdd):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()
    return {"status": "OK"}

@router.get("/only_auth")
async def only_auth(request: Request):
    # try:
    #     return request.cookies["access_token"]
    # except:
    #     return None
    # cookies = request.cookies
    return request.cookies['access_token'] if 'access_token' in request.cookies else None

