from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.bot.schemas.product_schema import ProductSchemaRead, ProductSchemaBase
from src.infrastructure.database.models.products_model import Product


class ProductsRepoImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Product

    async def get_all(self) -> list:
        stmt = sa.select(self.model)
        result = await self.session.execute(stmt)
        products = result.scalars().all()
        return [ProductSchemaBase.model_validate(row) for row in products]

    async def get_by_category(self, category_id: int) -> list[ProductSchemaBase]:
        stmt = sa.select(self.model).where(self.model.category_id == category_id)
        result = await self.session.execute(stmt)
        products = result.scalars().all()
        return [ProductSchemaBase.model_validate(product) for product in products]

    async def get_by_id(self, product_id: int) -> ProductSchemaBase:
        query = (
            sa.select(self.model).where(self.model.id == product_id).with_for_update()
        )
        execute = await self.session.execute(query)
        result = execute.scalar_one()

        return ProductSchemaBase.model_validate(result)

    async def add(self, product: ProductSchemaRead) -> ProductSchemaBase:
        stmt = sa.insert(self.model).values(product.model_dump()).returning(self.model)
        model = await self.session.execute(stmt)
        result = model.scalar_one()
        return ProductSchemaBase.model_validate(result)

    async def update(self, product: ProductSchemaBase) -> ProductSchemaBase:
        stmt = (
            sa.update(self.model)
            .where(self.model.id == product.id)
            .values(product.model_dump(exclude_defaults=True))
            .returning(self.model)
        )
        execute = await self.session.execute(stmt)
        result = execute.scalar_one()
        return ProductSchemaBase.model_validate(result)

    async def delete(self, products_id) -> ProductSchemaBase:
        stmt = (
            sa.delete(self.model)
            .where(self.model.id == products_id)
            .returning(self.model)
        )
        execute = await self.session.execute(stmt)
        result = execute.scalar_one()
        return ProductSchemaBase.model_validate(result)
