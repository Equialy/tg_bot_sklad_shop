from pydantic import ConfigDict, AliasGenerator, BaseModel, Field




class ProductSchemaRead(BaseModel):
    name: str
    description: str
    category_id: int

    model_config = ConfigDict(from_attributes=True)


class ProductSchemaBase(ProductSchemaRead):
   id: int