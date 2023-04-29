from app.models.hotels import HotelOrm
from app.schemas.hotels import Hotel
from app.repositories.base import BaseReposirory
from sqlalchemy import select

class HotelRepository(BaseReposirory):
    model = HotelOrm
    schema = Hotel

    async def get_all(
            self,
            location,
            title,
            limit,
            offset,
            ) -> list[Hotel]:
        query = select(self.model)
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
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [Hotel.model_validate(hotel, from_attributes=True) for hotel in result.scalars().all()]


