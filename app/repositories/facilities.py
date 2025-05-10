from app.repositories.base import BaseReposirory
from app.models.facilities import FacilitiesOrm
from app.schemas.facilities import Facilities


class FacilitiesRepository(BaseReposirory):
    model = FacilitiesOrm
    schema = Facilities

