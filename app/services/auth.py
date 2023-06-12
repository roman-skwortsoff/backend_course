from datetime import timezone, timedelta, datetime

from fastapi import HTTPException, Response
from passlib.context import CryptContext
import jwt

from app.config import settings
from app.exceptions import IncorrectPasswordException, ObjectAlreadyExistException, UserAlreadyExistException, \
    NotTokenException, ObjectNotFoundException
from app.schemas.users import UserRequestAdd, UserAdd
from app.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode |= {"exp": expire}
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password):
        verify = self.pwd_context.verify(plain_password, hashed_password)
        if verify:
            return True
        raise IncorrectPasswordException

    def decode_token(self, token: str) -> dict:
        try:
            decoded = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return decoded
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Токен истек")
        except Exception as e:
            raise HTTPException(
                status_code=401, detail=f"Ошибка при декодировании токена: {str(e)}"
            )

    async def login_user(self, data: UserRequestAdd, response: Response):
        user = await self.db.users.get_user_with_hashed_password(email=data.email)
        self.verify_password(data.password, user.password)
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return access_token


    async def register_user(self, data: UserRequestAdd,):
        hashed_password = self.hash_password(data.password)
        new_user_data = UserAdd(email=data.email, password=hashed_password)
        try:
            await self.db.users.add(new_user_data)
        except ObjectAlreadyExistException:
            raise UserAlreadyExistException
        await self.db.commit()

    async def get_user(self, user_id: int):
        try:
            return await self.db.users.get_one(id=user_id)
        except ObjectNotFoundException:
            raise NotTokenException

    async def logout_user(self, response: Response):
        response.delete_cookie("access_token")