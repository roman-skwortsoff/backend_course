from app.schemas.bookings import BookingAddData, BookingAdd
from app.services.base import BaseService
from app.services.rooms import RoomService


class BookingService(BaseService):

    async def get_bookings(self):
        return await self.db.bookings.get_all()

    async def get_user_bookings(self, user_id: int):
        return await self.db.bookings.get_filtered(user_id=user_id)

    async def create_booking(self, user_id: int, booking_data: BookingAdd):
        room = await RoomService(self.db).get_room_with_check(booking_data.room_id)
        merged_data = BookingAddData(
            **booking_data.model_dump(), price=room.price, user_id=user_id
        )
        booking = await self.db.bookings.add_booking(merged_data, hotel_id=room.hotel_id)
        await self.db.commit()
        return booking

    async def delete_booking(self, booking_id: int, user_id: int) -> None:
        await self.db.bookings.delete(id=booking_id, user_id=user_id)
        await self.db.commit()
