from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.bot.schemas.variant_schema import VariantSchemaRead, VariantSchemaBase
from src.infrastructure.database.models.products_model import Variant


class VariantRepositoryImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Variant

    async def add(self, item: VariantSchemaRead) -> VariantSchemaBase:
        stmt = sa.insert(self.model).values(item.model_dump()).returning(self.model)
        model = await self.session.execute(stmt)
        result = model.scalar_one()
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
