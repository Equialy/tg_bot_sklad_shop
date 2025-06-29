from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.bot.schemas.variant_schema import VariantSchemaRead, VariantSchemaBase
from src.infrastructure.database.models.products_model import Variant


class VariantRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Variant

    async def get_all(self) -> list[VariantSchemaBase]:
        stmt = sa.select(self.model)
        model = await self.session.execute(stmt)
        result = model.scalars().all()
        return [VariantSchemaBase.model_validate(variant) for variant in result]

    async def add(self, item: VariantSchemaRead) -> VariantSchemaBase:
        stmt = sa.insert(self.model).values(item.model_dump()).returning(self.model)
        model = await self.session.execute(stmt)
        result = model.scalar_one()
        return VariantSchemaBase.model_validate(result)

    async def get_by_id_variant(self, variant_id: int) -> VariantSchemaBase:
        query = (
            sa.select(self.model).where(self.model.id == variant_id).with_for_update()
        )
        execute = await self.session.execute(query)
        result = execute.scalar()
        return VariantSchemaBase.model_validate(result)

    async def get_by_id_product(self, product_id: int) -> list[VariantSchemaBase]:
        query = (
            sa.select(self.model)
            .where(self.model.product_id == product_id)
            .with_for_update()
        )
        execute = await self.session.execute(query)
        result = execute.scalars().all()

        return [VariantSchemaBase.model_validate(item) for item in result]

    async def update(self, variant: VariantSchemaBase) -> VariantSchemaBase:
        stmt = (
            sa.update(self.model)
            .where(self.model.id == variant.id)
            .values(variant.model_dump(exclude_defaults=True))
            .returning(self.model)
        )
        execute = await self.session.execute(stmt)
        result = execute.scalar_one()
        return VariantSchemaBase.model_validate(result)
