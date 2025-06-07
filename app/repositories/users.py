from pydantic import EmailStr
from sqlalchemy import select

from app.models.users import UsersOrm
from app.repositories.base import BaseReposirory
from app.repositories.mappers.mappers import UserDataMapper
from app.schemas.users import UseWithHashedPassword


class UsersRepository(BaseReposirory):
    model = UsersOrm
    mapper = UserDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        result = await self.session.execute(query)
        model = result.scalars().one()
        return UseWithHashedPassword.model_validate(model)
