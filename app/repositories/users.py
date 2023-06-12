from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app.exceptions import UserNotFoundException
from app.models.users import UsersOrm
from app.repositories.base import BaseReposirory
from app.repositories.mappers.mappers import UserDataMapper
from app.schemas.users import UserWithHashedPassword


class UsersRepository(BaseReposirory):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise UserNotFoundException
        return UserWithHashedPassword.model_validate(model)
