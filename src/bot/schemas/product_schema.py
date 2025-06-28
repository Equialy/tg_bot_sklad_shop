from pydantic import ConfigDict, AliasGenerator, BaseModel, Field




class ProductSchemaRead(BaseModel):
    name: str = None
    description: str = None
    category_id: int = None

    model_config = ConfigDict(from_attributes=True)


class ProductSchemaBase(ProductSchemaRead):
   id: int