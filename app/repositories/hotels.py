from datetime import date
from sqlalchemy import select

from app.models.hotels import HotelOrm
from app.models.rooms import RoomsOrm
from app.repositories.utils import rooms_ids_for_booking
from app.schemas.hotels import Hotel
from app.repositories.base import BaseReposirory


class HotelRepository(BaseReposirory):
    model = HotelOrm
    schema = Hotel


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
        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]



