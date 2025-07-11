from datetime import date

from app.schemas.hotels import HotelAdd, HotelPATCH, Hotel
from app.services.base import BaseService
from app.exceptions import (
    check_date_to_after_date_from,
    ObjectNotFoundException,
    HotelNotFoundException,
)


class HotelService(BaseService):
    async def get_filtered_by_time(
        self,
        pagination,
        date_from: date,
        date_to: date,
        location: str | None,
        title: str | None,
    ):
        check_date_to_after_date_from(date_from=date_from, date_to=date_to)
        per_page = pagination.per_page or 5
        return await self.db.hotels.get_filtered_by_date(
            date_from=date_from,
            date_to=date_to,
            location=location,
            title=title,
            limit=per_page or 5,
            offset=per_page * (pagination.page - 1),
        )

    async def get_hotel(self, hotel_id: int):
        hotel = await self.db.hotels.get_one(id=hotel_id)
        return hotel

    async def create_hotel(self, hotel_data: HotelAdd):
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return hotel

    async def put_hotel(self, hotel_id: int, hotel_data: HotelAdd) -> None:
        await self.db.hotels.edit(hotel_data, id=hotel_id)
        await self.db.commit()

    async def patch_hotel(self, hotel_id: int, hotel_data: HotelPATCH) -> None:
        await self.db.hotels.edit(hotel_data, is_patch=True, id=hotel_id)
        await self.db.commit()

    async def delete_hotel(self, hotel_id: int) -> None:
        await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()

    async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
        try:
            return await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException
