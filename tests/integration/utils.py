from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_from_db_by_pk(
    async_session_factory: async_sessionmaker[AsyncSession], orm_model, primary_key
) -> Any:
    async with async_session_factory() as session:
        return await session.get(orm_model, primary_key)


async def get_from_db_by_filter(
    async_session_factory: async_sessionmaker[AsyncSession],
    orm_model,
    filters,
    scalar: bool = False,
):
    async with async_session_factory() as session:
        stmt = select(orm_model).where(*filters)
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
