from typing import Any, overload

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


@overload
async def get_from_db_by_pk[OrmT](
    async_session_factory: async_sessionmaker[AsyncSession],
    orm_model: type[OrmT],
    primary_key: Any,
) -> OrmT | None: ...


@overload
async def get_from_db_by_pk[OrmT, SchemaT: BaseModel](
    async_session_factory: async_sessionmaker[AsyncSession],
    orm_model: type[OrmT],
    primary_key: Any,
    model_for_validation: type[SchemaT],
) -> SchemaT | None: ...


async def get_from_db_by_pk[OrmT, SchemaT: BaseModel](
    async_session_factory: async_sessionmaker[AsyncSession],
    orm_model: type[OrmT],
    primary_key: Any,
    model_for_validation: type[SchemaT] | None = None,
) -> OrmT | SchemaT | None:

    async with async_session_factory() as session:
        res = await session.get(orm_model, primary_key)

        if res is None:
            return None

        if model_for_validation:
            return model_for_validation.model_validate(res)

        return res


async def get_from_db_by_filter(
    async_session_factory: async_sessionmaker[AsyncSession],
    orm_model,
    filters=None,
    scalar: bool = False,
):
    async with async_session_factory() as session:
        stmt = select(orm_model)
        if filters:
            stmt = stmt.where(*filters)
        res = await session.execute(stmt)
        if scalar:
            return res.scalar_one_or_none()
        else:
            return res.scalars().all()


async def create_entity(
    async_session_factory: async_sessionmaker[AsyncSession], orm_model
):
    async with async_session_factory() as session:
        try:
            session.add(orm_model)
            await session.commit()
            await session.refresh(orm_model)
            return orm_model
        except IntegrityError:
            await session.rollback()
            raise
