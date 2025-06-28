from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.bot.schemas.product_schema import ProductSchemaRead, ProductSchemaBase
from src.infrastructure.database.models.products_model import Product


class ProductsRepoImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Product

    async def add(self, product: ProductSchemaRead) -> ProductSchemaBase:
        stmt = sa.insert(self.model).values(product.model_dump()).returning(self.model)
        model = await self.session.execute(stmt)
        result = model.scalar_one()
        return ProductSchemaBase.model_validate(result)
