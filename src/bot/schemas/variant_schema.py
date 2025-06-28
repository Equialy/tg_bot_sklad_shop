from pydantic import BaseModel
from pydantic import ConfigDict, AliasGenerator, BaseModel, Field


class VariantSchemaRead(BaseModel):
    product_id: int
    sku: str
    price: float
    stock: int
    description: str
    photo1: str
    photo2: str
    model_config = ConfigDict(from_attributes=True)



class VariantSchemaBase(VariantSchemaRead):
    id: int

