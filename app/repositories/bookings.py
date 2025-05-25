from datetime import date

from sqlalchemy import select

from app.models.bookings import BookingsOrm
from app.repositories.base import BaseReposirory
from app.repositories.mappers.mappers import BookingDataMapper


class BookingsRepository(BaseReposirory):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_booking_with_today_checkin(self):
        query = (select(BookingsOrm)
                 .filter(BookingsOrm.date_from == date.today())
                 )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]
