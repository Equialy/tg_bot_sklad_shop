from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.keyboards.inline_keyboards import get_callback_btns
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.bot.states.states import AddItemProduct
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl
from src.infrastructure.database.repositories.variant_repo import VariantRepositoryImpl

admin_variant_router = Router(name=__name__)
admin_variant_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_variant_router.callback_query(F.data.startswith("select_variants_"))
async def select_variant(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.answer()
    variants = await VariantRepositoryImpl(session=session).get_all()
    for item in variants:
        media = [InputMediaPhoto(media=item.photo1), InputMediaPhoto(media=item.photo2)]

        await callback.message.answer_media_group(media=media)

        await callback.message.answer(
            text=f"Товары по данной модели: "
            f"Описание: \n{markdown.hbold(item.description)}\n"
            f"Цена: {markdown.hbold(item.price)}\n"
            f"В наличии: {markdown.hbold(item.stock)}\n"
            f"Sku: {markdown.hbold(item.sku)}\n"
            f"ID product: {markdown.hbold(item.product_id)}\n",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить вариант товара": f"delete_variant_{item.id}",
                    f"Изменить": f"variant_update_{item.id}",
                }
            ),
        )


@admin_variant_router.callback_query(
    StateFilter(None), F.data.startswith("variant_update_")
)
async def variant_update(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.answer()
    await state.set_state(AddItemProduct.product_id)
    AddItemProduct.item_for_update = await VariantRepositoryImpl(
        session=session
    ).get_by_id_variant(variant_id=int(callback.data.split("_")[-1]))
    product = await ProductsRepoImpl(session=session).get_all()
    buttons = [f"{c.id} — {c.name}" for c in product]
    await callback.message.answer(
        text="Если хотите пропустить поле введите: далее" "Введите модель",
        reply_markup=get_reply_keyboard(*buttons, size=(2,)),
    )
