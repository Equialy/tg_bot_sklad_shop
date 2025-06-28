from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.keyboards.inline_keyboards import get_callback_btns
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.schemas.product_schema import ProductSchemaRead, ProductSchemaBase
from src.bot.schemas.variant_schema import VariantSchemaRead
from src.bot.states.states import AddProduct, AddItemProduct

from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl
from src.infrastructure.database.repositories.variant_repo import VariantRepositoryImpl

admin_add_item_product = Router(name=__name__)
admin_add_item_product.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_add_item_product.callback_query(
    AddItemProduct.product_id, F.data.startswith("product_id_")
)
async def add_name_item(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(product_id=int(callback.data.split("_")[-1]))
    await state.set_state(AddItemProduct.description)
    await callback.message.answer(text="Введите описание товара")


@admin_add_item_product.message(AddItemProduct.description, F.text)
async def add_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(AddItemProduct.price)
    await message.answer(text="Введите цену")


@admin_add_item_product.message(AddItemProduct.price, F.text)
async def add_price_item(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AddItemProduct.stock)
    await message.answer(text="Введите количество")


@admin_add_item_product.message(AddItemProduct.stock, F.text)
async def add_stock_item(message: types.Message, state: FSMContext):
    await state.update_data(stock=message.text)
    await state.set_state(AddItemProduct.photo1)
    await message.answer(text="Добавте фото 1")


@admin_add_item_product.message(AddItemProduct.photo1, F.photo)
async def add_photo_item(message: types.Message, state: FSMContext):
    await state.update_data(photo1=message.photo[-1].file_id)
    await state.set_state(AddItemProduct.photo2)
    await message.answer(text="Добавте второе фото")


@admin_add_item_product.message(AddItemProduct.photo1)
async def add_photo_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте фото")


@admin_add_item_product.message(AddItemProduct.photo2, F.photo)
async def add_photo_2_item(message: types.Message, state: FSMContext):
    await state.update_data(photo2=message.photo[-1].file_id)
    await state.set_state(AddItemProduct.sku)
    await message.answer(text="Введите sku")


@admin_add_item_product.message(AddItemProduct.photo2)
async def add_photo_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте фото")


@admin_add_item_product.message(AddItemProduct.sku, F.text)
async def add_sku_item(message: types.Message, state: FSMContext):
    await state.update_data(sku=message.text)
    await state.set_state(AddItemProduct.confirmation)
    data = await state.get_data()
    await message.answer(
        f"Создать товар?"
        f"\n\nID: <b>{data["product_id"]}</b>"
        f"\nОписание: <b>{data["description"]}</b>\n\n"
        f"\nЦена: <b>{data["price"]}</b>\n\n"
        f"\nКоличетсво: <b>{data["stock"]}</b>\n\n"
        f"\nФото 1: <b>{data["photo1"]}</b>\n\n"
        f"\nФото 2: <b>{data["photo2"]}</b>\n\n"
        f"\nsku: <b>{data["sku"]}</b>\n\n"
        "✅ — Да, создать\n❌ — Отмена",
        reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
    )


@admin_add_item_product.message(AddItemProduct.confirmation)
async def save_to_db_item_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    # достаём из state остальные поля (name, description и т.д.)
    if message.text == "✅ Да":
        data = await state.get_data()
        product = VariantSchemaRead(
            product_id=data["product_id"],
            sku=data["sku"],
            price=data["price"],
            stock=data["stock"],
            description=data["description"],
            photo1=data["photo1"],
            photo2=data["photo2"],
        )
        add_item_product = await VariantRepositoryImpl(session=session).add(product)
        await message.answer(
            f"Товар «{add_item_product.description}» \n{add_item_product.photo1} \nуспешно создан в категории {add_item_product.product_id}.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer(str(data))
    else:
        await message.answer(
            "Создание продукта отменено.", reply_markup=types.ReplyKeyboardRemove()
        )
    await state.clear()
