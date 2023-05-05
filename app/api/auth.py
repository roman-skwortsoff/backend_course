from fastapi import APIRouter, HTTPException, Response, Request

from app.api.dependencies import UserIdDep, DBDep
from app.database import async_session_maker
from app.repositories.users import UsersRepository
from app.schemas.users import UserRequestAdd, UserAdd
from app.services.auth import AuthService


router = APIRouter(prefix='/auth', tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(
        data: UserRequestAdd,
        response: Response,
        db: DBDep
):
    user = await db.users.get_user_with_hashed_password(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Пользователь с таким email не зарегистрирован")
    if not AuthService().verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Пароль неверный")
    access_token = AuthService().create_access_token({"user_id": user.id})
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.post("/register")
async def register_user(data: UserRequestAdd, db: DBDep):
    hashed_password = AuthService().hash_password(data.password)
    new_user_data = UserAdd(email=data.email, password=hashed_password)
    await db.users.add(new_user_data)
    await db.commit()
    return {"status": "OK"}


@router.get("/me")
async def get_me(
        user_id: UserIdDep,
        db: DBDep
):
    user = await db.users.get_one_or_none(id=user_id)
    return user


@router.post("/logout")
async def logout_user(
        response: Response,
        db: DBDep
):
    response.delete_cookie("access_token")
    await db.commit()
    return {"status": "OK"}