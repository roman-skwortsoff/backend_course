from sqlalchemy import select, insert

from app.models.rooms import RoomsOrm
from app.repositories.base import BaseReposirory
from app.schemas.rooms import Room


class RoomsRepository(BaseReposirory):
    model = RoomsOrm
    schema = Room

    async def get_rooms_in_hotel(self, hotel_id: int):
        query = select(self.model).where(self.model.hotel_id == hotel_id)
        result = await self.session.execute(query)
        models = result.scalars().all()
        if not models:
            return None
        return [self.schema.model_validate(model, from_attributes=True) for model in models]


    async def get_all(
            self,
            description,
            title,
            limit,
            offset,
            ) -> list[Room]:
        query = select(self.model)
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
        return [Room.model_validate(room, from_attributes=True) for room in result.scalars().all()]



