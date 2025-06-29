from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter, IsAdmin
from src.bot.handlers.admin_handlers.add_banner_router import admin_banner_router
from src.bot.handlers.admin_handlers.add_item_product_model import (
    admin_add_item_product,
)
from src.bot.handlers.admin_handlers.add_model_router import admin_add_model
from src.bot.handlers.admin_handlers.handler_category import admin_router_category
from src.bot.handlers.admin_handlers.update_router import admin_router_update
from src.bot.handlers.admin_handlers.variant_router import admin_variant_router
from src.bot.keyboards.inline_keyboards import get_callback_btns, ADMIN_INLINE_KB
from src.bot.states.states import AddProduct, AddItemProduct

from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl

admin_router = Router(name=__name__)
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())
admin_router.include_routers(
    admin_add_model,
    admin_router_category,
    admin_router_update,
    admin_add_item_product,
    admin_banner_router,
    admin_variant_router,
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_INLINE_KB)


@admin_router.message(StateFilter("*"), Command("отмена"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "отмена")
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Действия отменены", reply_markup=ADMIN_INLINE_KB)


@admin_router.message(Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_state_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AddProduct.name:
        await message.answer(
            text="Предыдущего шага нет. Введите название товара или напишите отмена"
        )
        return
    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(
                f"Вы вернулись к предыдущему шагу \n {AddProduct.texts[previous.state]}"
            )
        previous = step


@admin_router.callback_query(StateFilter(None), F.data == "add_item_product")
async def add_item_product(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    await callback.answer()
    await state.set_state(AddItemProduct.product_id)
    products = await ProductsRepoImpl(session=session).get_all()
    await callback.message.answer(
        text=f"Выберите название продукта",
        reply_markup=get_callback_btns(
            btns={f"{product.name}": f"product_id_{product.id}" for product in products}
        ),
    )


@admin_router.callback_query(StateFilter(None), F.data.startswith("add_product"))
async def change_product(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AddProduct.name)
    await callback.answer()
    await callback.message.answer(text="Введите название товара")


@admin_router.callback_query(StateFilter(None), F.data.startswith("catalog_products"))
async def change_product(
    callback: types.CallbackQuery, state: FSMContext, session: AsyncSession
):
    products = await ProductsRepoImpl(session=session).get_all()
    await callback.message.answer(text="<strong>Cписок товаров </strong>")
    for idx, product in enumerate(products, start=1):
        await callback.answer()
        await callback.message.answer(
            f"{idx}  {product.name}\n {product.description}",
            reply_markup=get_callback_btns(
                btns={
                    "Удалить модель": f"delete_{product.id}",
                    "Изменить модель": f"update_{product.id}",
                    "Просмотреть варианты": f"select_variants_{product.id}",
                }
            ),
        )


@admin_router.callback_query(StateFilter(None), F.data.startswith("delete_"))
async def delete_product(callback: types.CallbackQuery, session: AsyncSession):
    data = callback.data.split("_")[-1]
    product = await ProductsRepoImpl(session=session).delete(int(data))
    await callback.answer()
    await callback.message.answer(text=f"Товар <strong>{product.name}</strong> удален")
