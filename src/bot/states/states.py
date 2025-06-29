from aiogram.fsm.state import StatesGroup, State

from src.bot.schemas.product_schema import ProductSchemaBase
from src.bot.schemas.variant_schema import VariantSchemaBase


class AddProduct(StatesGroup):
    category_id = State()
    name = State()
    description = State()
    waiting_variant = State()
    sku = State()
    price = State()
    stock = State()  # колличество
    photo1 = State()
    photo = State()
    confirmation = State()
    product_for_update: ProductSchemaBase | None = None
    update_confirmation = State()

    texts = {
        "AddProduct:name": "Введите название заново:",
        "AddProduct:description": "Введите описание заново:",
        "AddProduct:price": "Введите стоимость заново:",
        "AddProduct:photo": "Этот стейт последний, поэтому...",
    }


class AddCategoryProducts(StatesGroup):
    name = State()
    parent_id = State()
    confirmation = State()


class AddItemProduct(StatesGroup):
    product_id = State()
    sku = State()
    price = State()
    stock = State()
    description = State()
    photo1 = State()
    photo2 = State()
    item_for_update: VariantSchemaBase | None = None
    confirmation = State()
    update_confirmation = State()


class AddBanner(StatesGroup):
    name = State()
    description = State()
    image = State()
    confirmation = State()
