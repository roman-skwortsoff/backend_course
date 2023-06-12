from asyncpg import UniqueViolationError
from pydantic import BaseModel
import logging
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import NoResultFound, IntegrityError

from app.repositories.mappers.base import DataMapper
from app.exceptions import (
    ObjectNotFoundException,
    DataBaseIntegrityException,
    ObjectAlreadyExistException,
)


class BaseReposirory:
    model = None
    mapper: DataMapper = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [
            self.mapper.map_to_domain_entity(model) for model in result.scalars().all()
        ]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel):
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(add_stmt)
        except IntegrityError as ex:
            if isinstance(ex.orig.__cause__, UniqueViolationError):
                logging.exception(
                    f"Не удалось добавить данные в БД, входные данные={data}"
                )
                raise ObjectAlreadyExistException from ex
            else:
                logging.error(
                    f"Незнакомая ошибка добавления в БД>. Входные данные:{data}. Тип ошибки:{type(ex.orig.__cause__)=}"
                )
                raise DataBaseIntegrityException
        model = result.scalars().one()
        return self.mapper.map_to_domain_entity(model)

    async def add_bulk(self, data: list[BaseModel]):
        add_stmt = insert(self.model).values([item.model_dump() for item in data])
        try:
            await self.session.execute(add_stmt)
        except IntegrityError:
            raise DataBaseIntegrityException

    async def edit(self, data: BaseModel, is_patch: bool = False, **filter_by) -> None:
        await self.get_one(**filter_by)
        stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=is_patch))
        )
        await self.session.execute(stmt)

    async def delete(self, **filter_by) -> None:
        await self.get_one(**filter_by)
        stmt = delete(self.model).filter_by(**filter_by)
        try:
            await self.session.execute(stmt)
        except IntegrityError:
            raise DataBaseIntegrityException
