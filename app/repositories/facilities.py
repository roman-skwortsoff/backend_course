from pydantic import BaseModel
from sqlalchemy import insert, delete

from app.repositories.base import BaseReposirory
from app.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from app.schemas.facilities import Facility, RoomFacility


class FacilitiesRepository(BaseReposirory):
    model = FacilitiesOrm
    schema = Facility


class RoomsFacilitiesRepository(BaseReposirory):
    model = RoomsFacilitiesOrm
    schema = RoomFacility

    async def delete_by_room_and_facilities(self,
                                            room_id: int,
                                            facility_ids: list[int]
    ) -> None:
        stmt = delete(RoomsFacilitiesOrm).where(RoomsFacilitiesOrm.room_id == room_id,
                                           RoomsFacilitiesOrm.facility_id.in_(facility_ids))
        await self.session.execute(stmt)