from sqlalchemy import insert, delete, select

from app.repositories.base import BaseReposirory
from app.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from app.repositories.mappers.mappers import FacilityDataMapper, RoomFacilityDataMapper


class FacilitiesRepository(BaseReposirory):
    model = FacilitiesOrm
    mapper = FacilityDataMapper


class RoomsFacilitiesRepository(BaseReposirory):
    model = RoomsFacilitiesOrm
    mapper = RoomFacilityDataMapper

    async def set_facilities_by_room(self,
                                     room_id: int,
                                     facility_ids: list[int]
                                     ):
        get_facilities_ids = (select(RoomsFacilitiesOrm.facility_id)
                      .filter_by(room_id=room_id)
                      )
        res = await self.session.execute(get_facilities_ids)
        current_facilities_ids = res.scalars().all()
        ids_to_remove = list(set(current_facilities_ids) - set(facility_ids))
        ids_to_add = list(set(facility_ids) - set(current_facilities_ids))

        if ids_to_remove:
            delete_stmt = (delete(RoomsFacilitiesOrm)
                    .where(RoomsFacilitiesOrm.room_id == room_id,
                                                    RoomsFacilitiesOrm.facility_id.in_(ids_to_remove))
                    )
            await self.session.execute(delete_stmt)

        if ids_to_add:
            insert_stmt = (insert(RoomsFacilitiesOrm)
                    .values([{"room_id": room_id, "facility_id": f_id} for f_id in ids_to_add])
                    )
            await self.session.execute(insert_stmt)