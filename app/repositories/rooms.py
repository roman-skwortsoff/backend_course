from app.models.rooms import RoomsOrm
from app.repositories.base import BaseReposirory

class RoomsRepository(BaseReposirory):
    model = RoomsOrm


