from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from app.models.rooms import RoomsOrm
from app.repositories.base import BaseReposirory
from app.repositories.mappers.mappers import RoomDataMapper, RoomDataWithRelsMapper
from app.repositories.utils import rooms_ids_for_booking
from app.schemas.rooms import Room, RoomWithRels


class RoomsRepository(BaseReposirory):
    model = RoomsOrm
    mapper = RoomDataMapper


    async def get_rooms_in_hotel(self, hotel_id: int):
        query = (select(self.model)
                 .options(selectinload(self.model.facilities))
                 .where(self.model.hotel_id == hotel_id))
        result = await self.session.execute(query)
        models = result.scalars().all()
        if not models:
            return None
        return [RoomDataWithRelsMapper.map_to_domain_entity(model) for model in models]


    async def get_all_by_time(
            self,
            description,
            title,
            limit,
            offset,
            ) -> list[Room]:
        query = select(self.model).options(selectinload(self.model.facilities))
        if title:
            query = query.where(RoomsOrm.title
                                .ilike(f"%{title}%")
                                )
        if description:
            query = query.where(RoomsOrm.description
                                .ilike(f"%{description}%")
                                )
        query = (query
                .limit(limit)
                .offset(offset)
                )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(room) for room in result.scalars().all()]


    async def get_filtered_by_date(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date):

        rooms_ids_to_get = rooms_ids_for_booking(hotel_id=hotel_id, date_from=date_from, date_to=date_to)

        query = (
            select(self.model)
            .options(selectinload(self.model.facilities))
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )

        result = await self.session.execute(query)
        return [RoomDataWithRelsMapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_one_or_none(self, **filter_by):
        query = (select(self.model)
                 .options(selectinload(self.model.facilities))
                 .filter_by(**filter_by))
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return RoomDataWithRelsMapper.map_to_domain_entity(model)













