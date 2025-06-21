from datetime import date


from app.api.dependencies import PaginationDep
from app.schemas.facilities import RoomFacilityAdd
from app.schemas.rooms import RoomAdd, RoomAddData, RoomPATCH, RoomPatchData, Room
from app.services.base import BaseService
from app.exceptions import (
    check_date_to_after_date_from,
    ObjectNotFoundException,
    RoomNotFoundException,
)
from app.services.hotels import HotelService


class RoomService(BaseService):
    async def get_all_rooms(
        self,
        pagination: PaginationDep,
        description: str | None,
        title: str | None,
    ):
        per_page = pagination.per_page or 5
        return await self.db.rooms.get_all_rooms_in_hotels(
            description=description,
            title=title,
            limit=per_page or 5,
            offset=per_page * (pagination.page - 1),
        )

    async def get_rooms(
        self,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ):
        check_date_to_after_date_from(date_from=date_from, date_to=date_to)
        return await self.db.rooms.get_filtered_by_date(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )

    async def get_room(self, hotel_id: int, room_id: int):
        return await self.db.rooms.get_one(hotel_id=hotel_id, id=room_id)

    async def create_room(self, hotel_id: int, room_data: RoomAdd):
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
        room = await self.db.rooms.add(merged_data)
        room_facilities_data = [
            RoomFacilityAdd(room_id=room.id, facility_id=f_id)
            for f_id in room_data.facilities_ids
        ]
        await self.db.rooms_facilities.add_bulk(room_facilities_data)
        await self.db.commit()
        return room

    async def put_room(self, hotel_id: int, room_id: int, room_data: RoomAdd) -> None:
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        merged_data = RoomAddData(**room_data.model_dump(), hotel_id=hotel_id)
        try:
            await self.db.rooms.edit(merged_data, id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
        await self.db.rooms_facilities.set_facilities_by_room(
            room_id=room_id, facility_ids=room_data.facilities_ids
        )
        await self.db.commit()

    async def patch_room(
        self, hotel_id: int, room_id: int, room_data: RoomPATCH
    ) -> None:
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        room_data_dict = room_data.model_dump(exclude_unset=True)
        merged_data = RoomPatchData(**room_data_dict, hotel_id=hotel_id)
        try:
            await self.db.rooms.edit(merged_data, is_patch=True, id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException

        if "facilities_ids" in room_data_dict:
            await self.db.rooms_facilities.set_facilities_by_room(
                room_id=room_id, facility_ids=room_data_dict["facilities_ids"]
            )
        await self.db.commit()

    async def delete_room(self, hotel_id: int, room_id: int) -> None:
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)
        # try:
        await self.db.rooms.delete(id=room_id, hotel_id=hotel_id)
        # except ObjectNotFoundException:
        #     raise RoomNotFoundException
        await self.db.commit()

    async def get_room_with_check(self, room_id: int) -> Room:
        try:
            return await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
