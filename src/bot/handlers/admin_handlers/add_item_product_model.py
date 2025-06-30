from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.keyboards.inline_common_buttons import ADMIN_INLINE_KB
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.schemas.variant_schema import VariantSchemaRead, VariantSchemaBase
from src.bot.states.states import AddItemProduct

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


# 2) Обработка текстового «далее» (Message), когда вы хотите пропустить
@admin_add_item_product.message(AddItemProduct.product_id, F.text == "далее")
async def add_name_item_skip(callback: types.Message, state: FSMContext):
    data = AddItemProduct.item_for_update
    if not data:
        await callback.answer(
            "Вы сейчас не в изменении товара", reply_markup=ADMIN_INLINE_KB
        )
        await state.clear()
        return
    await state.update_data(product_id=data.product_id)
    await state.set_state(AddItemProduct.description)
    await callback.answer("Пропускаем выбор модели, введите описание товара")


@admin_add_item_product.message(
    AddItemProduct.description, or_f((F.text), (F.text == "Далее"))
)
async def add_description(message: types.Message, state: FSMContext):
    if message.text.strip() == "далее" and AddItemProduct.item_for_update != None:
        await state.update_data(description=AddItemProduct.item_for_update.description)
    else:
        await state.update_data(description=message.text)
    await state.set_state(AddItemProduct.price)
    await message.answer(text="Введите цену")


@admin_add_item_product.message(
    AddItemProduct.price, or_f((F.text), (F.text == "Далее"))
)
async def add_price_item(message: types.Message, state: FSMContext):
    if message.text.strip() == "далее" and AddItemProduct.item_for_update != None:
        await state.update_data(price=AddItemProduct.item_for_update.price)
    else:
        await state.update_data(price=message.text)
    await state.set_state(AddItemProduct.stock)
    await message.answer(text="Введите количество")


@admin_add_item_product.message(
    AddItemProduct.stock, or_f((F.text), (F.text == "далее"))
)
async def add_stock_item(message: types.Message, state: FSMContext):
    if message.text.strip() == "далее" and AddItemProduct.item_for_update != None:
        await state.update_data(stock=AddItemProduct.item_for_update.stock)
    else:
        await state.update_data(stock=message.text)
    await state.set_state(AddItemProduct.photo1)
    await message.answer(text="Добавте фото 1")


@admin_add_item_product.message(
    AddItemProduct.photo1, or_f((F.photo), (F.text == "далее"))
)
async def add_photo_item(message: types.Message, state: FSMContext):
    if not message.photo:
        if message.text.strip() == "далее" and AddItemProduct.item_for_update != None:
            await state.update_data(photo1=AddItemProduct.item_for_update.photo1)
    else:
        await state.update_data(photo1=message.photo[-1].file_id)
    await state.set_state(AddItemProduct.photo2)
    await message.answer(text="Добавте второе фото")


@admin_add_item_product.message(AddItemProduct.photo1)
async def add_photo_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте фото")


@admin_add_item_product.message(
    AddItemProduct.photo2, or_f((F.photo), (F.text == "далее"))
)
async def add_photo_2_item(message: types.Message, state: FSMContext):
    if not message.photo:
        if message.text.strip() == "далее" and AddItemProduct.item_for_update != None:
            await state.update_data(photo2=AddItemProduct.item_for_update.photo2)
    else:
        await state.update_data(photo2=message.photo[-1].file_id)
    await state.set_state(AddItemProduct.sku)
    await message.answer(text="Введите sku")


@admin_add_item_product.message(AddItemProduct.photo2)
async def add_photo_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте фото")


@admin_add_item_product.message(AddItemProduct.sku, or_f((F.text), (F.text == "далее")))
async def add_sku_item(message: types.Message, state: FSMContext):
    if message.text.strip() == "далее" and AddItemProduct.item_for_update != None:
        await state.update_data(sku=AddItemProduct.item_for_update.sku)
    else:
        await state.update_data(sku=message.text)
    await state.set_state(AddItemProduct.confirmation)
    data = await state.get_data()
    if AddItemProduct.item_for_update:
        await state.set_state(AddItemProduct.update_confirmation)
        await message.answer(
            text=f"Изменить вариант товара?\n\n"
            f"\n\nID: <b>{data["product_id"]}</b>"
            f"\nОписание: <b>{data["description"]}</b>\n\n"
            f"\nЦена: <b>{data["price"]}</b>\n\n"
            f"\nКоличетсво: <b>{data["stock"]}</b>\n\n"
            f"\nФото 1: <b>{data["photo1"]}</b>\n\n"
            f"\nФото 2: <b>{data["photo2"]}</b>\n\n"
            f"\nsku: <b>{data["sku"]}</b>\n\n"
            "✅ — Да, изменить\n❌ — Отмена",
            reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
        )
    else:
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


@admin_add_item_product.message(AddItemProduct.update_confirmation)
async def update_done(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if message.text == "✅ Да":
        product = await VariantRepositoryImpl(session=session).update(
            VariantSchemaBase(
                id=AddItemProduct.item_for_update.id,
                product_id=data["product_id"],
                sku=data["sku"],
                price=data["price"],
                stock=data["stock"],
                description=data["description"],
                photo1=data["photo1"],
                photo2=data["photo2"],
            )
        )
        await message.answer(
            text=f"Товар изменен:\n\n"
            f"Описание: {product.description}\n"
            f"ID Product: {product.product_id}\n"
            f"ID Количество: {product.stock}\n"
            f"ID Цена: {product.price}\n"
            f"ID Фото 1: {product.photo1}\n"
            f"ID Фото 2: {product.photo2}\n",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Изменение продукта отменено.", reply_markup=types.ReplyKeyboardRemove()
        )
    AddItemProduct.item_for_update = None
    await state.clear()
