from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin

from src.bot.keyboards.inline_common_buttons import get_callback_btns, ADMIN_INLINE_KB
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.schemas.banner_schema import BannerSchemaRead
from src.bot.states.states import AddBanner, DeleteBanner
from src.infrastructure.database.repositories.banner_repo import BannerRepoImpl

admin_banner_delete_router = Router(name=__name__)
admin_banner_delete_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_banner_delete_router.callback_query(StateFilter(None), F.data == "delete_banner")
async def page_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(DeleteBanner.name)
    await callback.message.answer(
        text="Введите название страницы баннера, например: \n"
        "main, category, catalog ..."
    )
    await callback.answer()


@admin_banner_delete_router.message(StateFilter(DeleteBanner.name), F.text)
async def confirm_delete(
    message: types.Message, state: FSMContext, session: AsyncSession
):

    await state.update_data(name=message.text)
    page_name = await BannerRepoImpl(session=session).get_banner(page=message.text)
    if page_name:
        await state.set_state(DeleteBanner.confirmation)
        await message.answer_photo(
            photo=page_name.image,
            caption=f"Удалиь баннер?"
            f"\n\nНазвание: <b>{page_name.name}</b>"
            f"\nОписание: <b>{page_name.description}</b>\n\n"
            "✅ — Да, удалить\n❌ — Отмена",
            reply_markup=get_callback_btns(
                btns={"✅ Да": "yes", "❌ Отмена": "cancel"}
            ),
        )
    else:
        await message.answer(text="Баннер не найден")
        await state.clear()
        return


@admin_banner_delete_router.callback_query(DeleteBanner.confirmation, F.data)
async def delete_from_db_banner(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.answer()

    data = await state.get_data()
    if callback.data == "yes":
        banner_delete = await BannerRepoImpl(session=session).delete(page=data["name"])
        await callback.message.answer(
            text=f"Баннер удален\n"
            f"{banner_delete.name}\n"
            f"{banner_delete.description}"
        )
    else:
        await callback.message.answer(text="Удаление отменено")
    await state.clear()
