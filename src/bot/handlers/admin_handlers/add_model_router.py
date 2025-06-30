from aiogram import Router, types, F
from aiogram.filters import or_f
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.keyboards.inline_common_buttons import ADMIN_INLINE_KB
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.schemas.product_schema import ProductSchemaRead
from src.bot.states.states import AddProduct

from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl

admin_add_model = Router(name=__name__)
admin_add_model.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_add_model.message(AddProduct.name, or_f(F.text, F.text == "далее"))
async def add_name_product(message: types.Message, state: FSMContext):
    if message.text.strip() == "далее" and AddProduct.product_for_update != None:
        await state.update_data(name=AddProduct.product_for_update.name)
    if message.text.strip() == "далее" and AddProduct.product_for_update == None:
        await message.answer(
            text="Вы сейчас не в измененнии товара", reply_markup=ADMIN_INLINE_KB
        )
        await state.clear()
        return
    else:
        await state.update_data(name=message.text)
    await message.answer(
        text="Введите описание товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.description)


@admin_add_model.message(AddProduct.name)
async def exc_name_product(message: types.Message, state: FSMContext):
    await message.answer(
        text="Введены не корректные данные. Введите название товара",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@admin_add_model.message(AddProduct.description, or_f(F.text, F.text == "далее"))
async def add_description_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text.strip() == "далее" and AddProduct.product_for_update != None:
        await state.update_data(description=AddProduct.product_for_update.description)
    else:
        await state.update_data(description=message.text)
    cats = await CategoryRepositoryImpl(session=session).get_all()
    buttons = [f"{cat.id} — {cat.name}" for cat in cats]
    await state.set_state(AddProduct.category_id)
    await message.answer(
        text="Выберите категорию", reply_markup=get_reply_keyboard(*buttons, size=(2,))
    )


@admin_add_model.message(AddProduct.description)
async def exc_description_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введеные некорректные данные. Введите описание")


@admin_add_model.message(AddProduct.category_id, or_f(F.text, F.text == "далее"))
async def add_category_product(message: types.Message, state: FSMContext):
    text = message.text.strip()
    if message.text.strip() == "далее" and AddProduct.product_for_update != None:
        await state.update_data(category_id=AddProduct.product_for_update.category_id)
    else:
        try:
            category_id = int(text.split("—", 1)[0].strip())
        except (IndexError, ValueError):
            await message.answer(
                "Неверный формат. Выберите категорию из списка кнопок."
            )
            return
        await state.update_data(category_id=category_id)
    await message.answer(text="Добавте цену", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(AddProduct.price)


@admin_add_model.message(AddProduct.category_id)
async def exc_category_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    categories = await CategoryRepositoryImpl(session=session).get_all()
    await message.answer(
        text="Введены не корректные данные. Выберите категорию",
        reply_markup=get_reply_keyboard(*categories, size=(2,)),
    )


@admin_add_model.message(AddProduct.price, or_f(F.text, F.text == "далее"))
async def add_price_product(message: types.Message, state: FSMContext):
    if message.text.strip() == "далее" and AddProduct.product_for_update != None:
        ...  # TODO price for product variant
    else:
        await state.update_data(price=message.text)
    await message.answer(text="Добавте изображение")
    await state.set_state(AddProduct.photo)


@admin_add_model.message(AddProduct.price)
async def exc_price_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте цену")


@admin_add_model.message(AddProduct.photo, or_f(F.photo, F.text == "далее"))
async def add_photo_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if message.text == "далее" and AddProduct.product_for_update != None:
        ...  # TODO photo for product variant
        await state.set_state(AddProduct.update_confirmation)
        await message.answer(
            text=f"Изменить товар?\n\n"
            f"Название: <b>{data["name"]}</b>"
            f"\nОписание: <b>{data["description"]}</b>\n\n"
            "✅ — Да, изменить\n❌ — Отмена",
            reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
        )
    else:
        if AddProduct.product_for_update:
            await state.set_state(AddProduct.update_confirmation)
            await message.answer(
                text=f"Изменить товар?\n\n"
                f"Название: <b>{data["name"]}</b>"
                f"\nОписание: <b>{data["description"]}</b>\n\n"
                "✅ — Да, изменить\n❌ — Отмена",
                reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
            )
        else:
            await state.update_data(photo=message.photo[-1].file_id)
            await message.answer(
                f"Создать товар?\n\nНазвание: <b>{data["name"]}</b>"
                f"\nОписание: <b>{data["description"]}</b>\n\n"
                "✅ — Да, создать\n❌ — Отмена",
                reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
            )
            await state.set_state(AddProduct.confirmation)


@admin_add_model.message(AddProduct.photo)
async def add_photo_product(message: types.Message, state: FSMContext):
    await message.answer(text="Введены не корректные данные. Добавте фото")


@admin_add_model.message(AddProduct.confirmation)
async def save_to_db_product(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    # достаём из state остальные поля (name, description и т.д.)
    if message.text == "✅ Да":
        data = await state.get_data()
        name = data["name"]
        description = data["description"]
        category_id = data["category_id"]
        product = ProductSchemaRead(
            name=name,
            description=description,
            category_id=category_id,
        )
        add_product = await ProductsRepoImpl(session=session).add(product)
        await message.answer(
            f"Товар «{add_product.name}» успешно создан в категории {add_product.category_id}.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer(str(data))
    else:
        await message.answer(
            "Создание продукта отменено.", reply_markup=types.ReplyKeyboardRemove()
        )
    AddProduct.product_for_update = None
    await state.clear()
