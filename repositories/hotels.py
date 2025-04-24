from app.models.hotels import HotelOrm
from repositories.base import BaseReposirory
from sqlalchemy import select

class HotelRepository(BaseReposirory):
    model = HotelOrm

    async def get_all(
            self,
            location,
            title,
            limit,
            offset,
            ):
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
        return result.scalars().all()


