from app.models.rooms import RoomsOrm
from repositories.base import BaseReposirory

class RoomsRepository(BaseReposirory):
    model = RoomsOrm


