from pydantic import BaseModel
from pydantic import ConfigDict, AliasGenerator, BaseModel, Field


class CategorySchemaRead(BaseModel):
    name: str
    parent_id: int | None = None

    model_config = ConfigDict(from_attributes=True)


class CategorySchemaBase(CategorySchemaRead):
    id: int
