from pydantic import BaseModel
from sqlalchemy import select, insert, update, delete
from app.database import engine


class BaseReposirory:
    model = None

    def __init__(self, session):
        self.session = session

    async def get_all(self, *args, **kwargs):
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    async def add(self, data):
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        print(add_stmt.compile(engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(add_stmt)
        return result.scalars().one_or_none()

    async def edit(self, id: int, data: BaseModel, **filter_by) -> None:
        print(id)
        print(data)
        stmt = (update(self.model)
            .where(self.model.id == id)
            .values(**data.model_dump())
                    )
        await self.session.execute(stmt)


    async def delete(self, id: int, **filter_by) -> None:
        stmt = delete(self.model).where(self.model.id == id)
        await self.session.execute(stmt)

