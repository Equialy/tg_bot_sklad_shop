from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.states.states import AddCategoryProducts

from src.infrastructure.database.models.products_model import Category
from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)

admin_router_category = Router(name=__name__)
admin_router_category.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_router_category.callback_query(StateFilter(None), F.data == "add_category")
async def add_category(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer(text="Введите название категории")
    await state.set_state(AddCategoryProducts.name)


@admin_router_category.message(AddCategoryProducts.name)
async def add_name_category(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    await state.update_data(name=message.text)
    cats = await CategoryRepositoryImpl(session=session).get_all()
    buttons = [f"{c.id} — {c.name}" for c in cats]
    buttons.append("Без родителя")

    await state.set_state(AddCategoryProducts.parent_id)
    await message.answer(
        "Выберите родительскую категорию или нажмите «Без родителя»:",
        reply_markup=get_reply_keyboard(*buttons, size=(2,)),
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
async def process_confirmation(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    if message.text == "✅ Да":
        data = await state.get_data()
        new_cat = Category(
            name=data["name"],
            parent_id=data["parent_id"],
        )
        session.add(new_cat)
        await message.answer(
            "Категория успешно создана!", reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "Создание категории отменено.", reply_markup=types.ReplyKeyboardRemove()
        )

    await state.clear()
