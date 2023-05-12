from datetime import date
from sqlalchemy import select

from app.models.hotels import HotelOrm
from app.models.rooms import RoomsOrm
from app.repositories.mappers.mappers import HotelDataMapper
from app.repositories.utils import rooms_ids_for_booking
from app.repositories.base import BaseReposirory


class HotelRepository(BaseReposirory):
    model = HotelOrm
    mapper = HotelDataMapper


    async def get_filtered_by_date(
            self,
            date_from: date,
            date_to: date,
            location,
            title,
            limit,
            offset,
    ):

        rooms_ids_to_get = rooms_ids_for_booking(date_from=date_from, date_to=date_to)
        hotel_ids_to_get = (
            select(RoomsOrm.hotel_id)
            .select_from(RoomsOrm)
            .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        )
        query = select(self.model).filter(HotelOrm.id.in_(hotel_ids_to_get))
        if title:
            query = query.where(HotelOrm.title
                                .ilike(f"%{title}%")
                                )
        if location:
            query = query.where(HotelOrm.location
                                .ilike(f"%{location}%")
                                )
        query = (query
                .limit(limit)
                .offset(offset)
                )
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(hotel) for hotel in result.scalars().all()]



