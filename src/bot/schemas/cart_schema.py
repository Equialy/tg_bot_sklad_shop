from pydantic import ConfigDict, AliasGenerator, BaseModel, Field

from src.bot.schemas.variant_schema import VariantSchemaBase


class CartSchemaRead(BaseModel):
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CartSchemaBase(CartSchemaRead):
    id: int


class CartItemSchemaRead(BaseModel):
    cart_id: int
    variant_id: int
    quantity: int
    variant: VariantSchemaBase

    model_config = ConfigDict(from_attributes=True)


class CartItemSchemaBase(CartItemSchemaRead):
    id: int
