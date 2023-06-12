from fastapi import APIRouter, Response

from app.api.dependencies import UserIdDep, DBDep
from app.exceptions import UserNotFoundException, UserNotFoundHTTPException, \
    IncorrectPasswordException, IncorrectPasswordHTTPException, UserAlreadyExistException, \
    UserAlreadyExistHTTPException, NotTokenException, NotTokenHTTPException
from app.schemas.users import UserRequestAdd
from app.services.auth import AuthService


router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(data: UserRequestAdd, response: Response, db: DBDep):
    try:
        access_token = await AuthService(db).login_user(data, response)
    except UserNotFoundException:
        raise UserNotFoundHTTPException
    except IncorrectPasswordException:
        raise IncorrectPasswordHTTPException
    return {"access_token": access_token}


@router.post("/register")
async def register_user(data: UserRequestAdd, db: DBDep):
    try:
        await AuthService(db).register_user(data)
    except UserAlreadyExistException:
        raise UserAlreadyExistHTTPException
    return {"status": "OK"}


@router.get("/me")
async def get_user(user_id: UserIdDep, db: DBDep):
    try:
        return await AuthService(db).get_user(user_id)
    except NotTokenException:
        raise NotTokenHTTPException


@router.post("/logout")
async def logout_user(response: Response, db: DBDep):
    await AuthService(db).logout_user(response)
    return {"status": "OK"}
