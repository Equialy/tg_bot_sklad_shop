from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin

from src.bot.keyboards.inline_keyboards import get_callback_btns, ADMIN_INLINE_KB
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.schemas.banner_schema import BannerSchemaRead
from src.bot.states.states import AddBanner
from src.infrastructure.database.repositories.banner_repo import BannerRepoImpl

admin_banner_router = Router(name=__name__)
admin_banner_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_banner_router.callback_query(StateFilter(None), F.data == "add_banner")
async def add_name_banner(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(AddBanner.name)
    await callback.message.answer(text="Введите название банера")


@admin_banner_router.message(AddBanner.name, F.text)
async def add_description_banner(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddBanner.image)
    await message.answer(text="Загрузите изображение банера")


@admin_banner_router.message(AddBanner.image, F.photo)
async def confirm_banner(message: types.Message, state: FSMContext):
    await state.update_data(image=message.photo[-1].file_id)
    await state.update_data(description=message.caption.strip())
    await state.set_state(AddBanner.confirmation)
    data = await state.get_data()
    await message.answer(
        f"Создать банер?"
        f"\n\nНазвание: <b>{data["name"]}</b>"
        f"\nОписание: <b>{data["description"]}</b>\n\n"
        f"\nИзображение: <b>{data["image"]}</b>\n\n"
        "✅ — Да, создать\n❌ — Отмена",
        reply_markup=get_reply_keyboard("✅ Да", "❌ Отмена"),
    )


@admin_banner_router.message(AddBanner.confirmation)
async def save_to_db_banner(
    message: types.Message, state: FSMContext, session: AsyncSession
):
    # достаём из state остальные поля (name, description и т.д.)
    if message.text == "✅ Да":
        data = await state.get_data()
        product = BannerSchemaRead(
            name=data["name"], description=data["description"], image=data["image"]
        )
        add_banner = await BannerRepoImpl(session=session).add_banner_description(
            product
        )
        await message.answer(
            f"Баннер «{add_banner.name}» \n{add_banner.image} \nуспешно создан с описанием {add_banner.image}.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        await message.answer(str(data))
    else:
        await message.answer(
            "Создание банера отменено.", reply_markup=types.ReplyKeyboardRemove()
        )
    await state.clear()
