from pydantic import ConfigDict, AliasGenerator, BaseModel, Field


class UserSchemaRead(BaseModel):
    telegram_id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserSchemaBase(UserSchemaRead):
    id: int
