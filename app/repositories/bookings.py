from datetime import date

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import select, insert
from starlette import status

from app.models import RoomsOrm
from app.models.bookings import BookingsOrm
from app.repositories.base import BaseReposirory
from app.repositories.mappers.mappers import BookingDataMapper, RoomDataMapper
from app.repositories.utils import rooms_ids_for_booking
from app.schemas.bookings import BookingAddData


class BookingsRepository(BaseReposirory):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_booking_with_today_checkin(self):
        query = (select(BookingsOrm)
                 .filter(BookingsOrm.date_from == date.today())
                 )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]

    async def add_booking(self, data: BookingAddData, hotel_id:int):

        rooms_ids_to_get = rooms_ids_for_booking(
            date_from=data.date_from,
            date_to=data.date_to,
            hotel_id=hotel_id
        )

        # 1е решение
        # stmt = select(rooms_ids_to_get.c.room_id)
        # result = await self.session.execute(stmt)
        # available_rooms_ids = [id for id in result.scalars().all()]

        # 2е решение
        # query = (
        #     select(RoomsOrm)
        #     .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        # )
        # result = await self.session.execute(query)
        # available_rooms = [RoomDataMapper.map_to_domain_entity(room) for room in result.scalars().all()]
        # available_rooms_ids = [room.id for room in available_rooms]

        # query = (
        #     select(RoomsOrm.id)
        #     .filter(RoomsOrm.id.in_(rooms_ids_to_get))
        # )
        result = await self.session.execute(rooms_ids_to_get)
        available_rooms_ids = [id for id in result.scalars().all()]

        if data.room_id in available_rooms_ids:
            booking = await self.add(data)
            return booking
        else:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Номер был забронирован"
            )
