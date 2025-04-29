from app.models.users import UsersOrm
from app.repositories.base import BaseReposirory
from app.schemas.users import User


class UsersRepository(BaseReposirory):
    model = UsersOrm
    schema = User


