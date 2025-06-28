from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.schemas.product_schema import ProductSchemaBase
from src.bot.states.states import AddProduct

from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl

admin_router_update = Router(name=__name__)
admin_router_update.message.filter(ChatTypeFilter(["private"]), IsAdmin())


@admin_router_update.callback_query(StateFilter(None), F.data.startswith("update_"))
async def update_product(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    AddProduct.product_for_update = await ProductsRepoImpl(session=session).get_by_id(
        product_id=int(callback.data.split("_")[-1])
    )
    await callback.answer()
    await callback.message.answer(
        text="Если хотите пропустить изменение поля введите: далее"
    )
    await callback.message.answer(
        text="Введите название товара", reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(AddProduct.name)


@admin_router_update.message(AddProduct.update_confirmation)
async def update_done(message: types.Message, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if message.text == "✅ Да":
        product = await ProductsRepoImpl(session=session).update(
            ProductSchemaBase(
                id=AddProduct.product_for_update.id,
                name=data["name"],
                description=data["description"],
            )
        )
        await message.answer(
            text=f"Товар изменен:\nНазвание: {markdown.hbold(product.name)}\n"
            f"Описание: {markdown.hbold(product.description)}\n"
            f"Категория: {markdown.hbold(product.category_id)}",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            "Изменение продукта отменено.", reply_markup=types.ReplyKeyboardRemove()
        )
    AddProduct.product_for_update = None
    await state.clear()
