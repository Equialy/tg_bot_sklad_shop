from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.states.states import AddProduct, AddCategoryProducts
from src.infrastructure.database.connection import get_async_session
import sqlalchemy as sa

from src.infrastructure.database.models.products_model import Category

admin_router_category = Router(name=__name__)
admin_router_category.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_router_category.message(StateFilter(None), F.text == "Добавить категорию")
async def add_category(message: types.Message, state: FSMContext):
    await message.answer(text="Введите название категории")
    await state.set_state(AddCategoryProducts.name)


@admin_router_category.message(AddCategoryProducts.name)
async def add_name_category(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    async with get_async_session() as session:
        cats = await session.execute(sa.select(Category.id, Category.name))
        categories = [f"{row.id} — {row.name}" for row in cats]
    await state.set_state(AddCategoryProducts.parent_id)
    await message.answer("Выберите родительскую категорию или нажмите «Без родителя»:",
                         reply_markup=get_reply_keyboard(*categories, "Без родителя", size=(2,))
                         )


@admin_router_category.message(AddCategoryProducts.parent_id)
async def process_parent(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = message.text.strip()
    if text == "Без родителя":
        parent_id = None
    else:
        # ожидаем, что пользователь нажал кнопку “<id> — <name>”
        parent_id = int(text.split("—", 1)[0].strip())
    await state.update_data(parent_id=parent_id)
    name = data["name"]
    parent_text = "нет" if parent_id is None else f"{parent_id}"
    await state.set_state(AddCategoryProducts.confirmation)
    await message.answer(
        f"Создать категорию?\n\nНазвание: <b>{name}</b>\nРодитель: <b>{parent_text}</b>\n\n"
        "✅ — Да, создать\n❌ — Отмена",
        reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
    )


@admin_router_category.message(AddCategoryProducts.confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    if message.text == "✅ Да":
        data = await state.get_data()
        async with get_async_session() as session:
            new_cat = Category(
                name=data["name"],
                parent_id=data["parent_id"],
            )
            session.add(new_cat)
            await session.commit()
        await message.answer("Категория успешно создана!", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer("Создание категории отменено.", reply_markup=types.ReplyKeyboardRemove())

    await state.clear()
