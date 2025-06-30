from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.bot.schemas.banner_schema import BannerSchemaRead, BannerSchemaBase
from src.infrastructure.database.models.banner_model import Banner


class BannerRepoImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Banner

    async def add_banner_description(self, data: BannerSchemaRead) -> BannerSchemaBase:
        # Добавляем новый или изменяем существующий по именам
        # пунктов меню: main, about, cart, shipping, payment, catalog
        query = sa.insert(self.model).values(data.model_dump()).returning(self.model)
        model = await self.session.execute(query)
        result = model.scalar_one()
        return BannerSchemaBase.model_validate(result)

    async def update_banner_image(
        self, name: str, image: str, description: str
    ) -> BannerSchemaBase:
        query = (
            sa.update(self.model)
            .where(self.model.name == name)
            .values(name=name, image=image, description=description)
            .returning(self.model)
        )
        execute = await self.session.execute(query)
        result = execute.scalar_one()
        return BannerSchemaBase.model_validate(result)

    async def get_banner(self, page: str) -> BannerSchemaBase | None:
        query = sa.select(self.model).where(self.model.name == page)
        model = await self.session.execute(query)
        result = model.scalar()
        if result is None:
            return None
        return BannerSchemaBase.model_validate(result)

    async def get_info_pages(self) -> list[BannerSchemaBase]:
        query = sa.select(self.model)
        model = await self.session.execute(query)
        result = model.scalars().all()
        return [BannerSchemaBase.model_validate(banner) for banner in result]

    async def delete(self, page: str) -> BannerSchemaBase:
        stmt = (
            sa.delete(self.model).where(self.model.name == page).returning(self.model)
        )
        execute = await self.session.execute(stmt)
        result = execute.scalar_one()
        return BannerSchemaBase.model_validate(result)
