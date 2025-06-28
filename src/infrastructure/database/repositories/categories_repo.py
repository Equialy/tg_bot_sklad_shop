from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.infrastructure.database.models.products_model import Category


class CategoryRepositoryProtocol(Protocol):
    async def get_all(self) -> list:
        ...

    async def add(self, *kwargs):
        ...


class CategoryRepositoryImpl(CategoryRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Category

    async def get_all(self) -> list:
        stmt = (
            sa.select(self.model)
        )
        result = await self.session.execute(stmt)
        cats = result.scalars().all()
        return [f"{row.id} — {row.name}" for row in cats]

    async def add(self, *kwargs):
        stmt = sa.insert(self.model).values(**kwargs).returning(self.model)
        model = await self.session.execute(stmt)
        result = model.scalar_one()
