from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.bot.schemas.user_schema import UserSchemaRead, UserSchemaBase
from src.infrastructure.database.models.users_model import Users


class UserRepoImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Users

    async def orm_add_user(self, user: UserSchemaRead) -> UserSchemaBase:
        query = sa.insert(self.model).values(user.model_dump()).returning(self.model)
        model = await self.session.execute(query)
        result = model.scalar_one()
        return UserSchemaBase.model_validate(result)
