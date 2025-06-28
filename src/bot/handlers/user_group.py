from aiogram import Router, types, Bot, F
from aiogram.filters import Command, CommandStart, or_f
from aiogram.types import InputMediaPhoto
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter
from src.bot.keyboards.inline_keyboards import get_callback_btns
from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl
from src.infrastructure.database.repositories.variant_repo import VariantRepositoryImpl

user_group_router = Router(name=__name__)
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))


@user_group_router.message(Command("admin"))
async def get_admin(message: types.Message, bot: Bot):
    chat_id = message.chat.id
    admin_list = await bot.get_chat_administrators(chat_id=chat_id)
    admin_list = [
        member.user.id
        for member in admin_list
        if member.status == "creator" or member.status == "administrator"
    ]
    bot.my_admins_list = admin_list
    if message.from_user.id in admin_list:
        await message.delete()


@user_group_router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(
        text=f"Добро пожаловать {message.from_user.username} в Slad Shop"
    )
    await message.answer(
        text=f"Каталог товаров",
        reply_markup=get_callback_btns(btns={"Каталог": "catalog", "Корзина": "carts"}),
    )


@user_group_router.callback_query(F.data == "catalog")
async def categories_products(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    categories = await CategoryRepositoryImpl(session=session).get_all()
    await callback.message.answer(
        text="Категории",
        reply_markup=get_callback_btns(
            btns={f"{cat.name}": f"category_id_{cat.id}" for cat in categories}
        ),
    )


@user_group_router.callback_query(F.data.startswith("category_id_"))
async def get_products_by_category(
    callback: types.CallbackQuery, session: AsyncSession
):
    await callback.answer()
    products = await ProductsRepoImpl(session=session).get_by_category(
        int(callback.data.split("_")[-1])
    )
    await callback.message.answer(
        text="Товары",
        reply_markup=get_callback_btns(
            btns={
                f"{product.name}": f"product_id_for_item_{product.id}"
                for product in products
            }
        ),
    )


@user_group_router.callback_query(F.data.startswith("product_id_for_item_"))
async def get_info_by_product(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    info_item = await VariantRepositoryImpl(session=session).get_by_id_product(
        product_id=int(callback.data.split("_")[-1])
    )
    for item in info_item:
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
                    "Добавить в корзину": f"add_to_cart_{item.id}",
                    f"Модель": f"category_id_{item.product_id}",
                }
            ),
        )


@user_group_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    ...


@user_group_router.callback_query(
    or_f(Command("catalog"), (F.data.startswith("catalog")))
)
async def catalog_handler_group(callback: types.CallbackQuery, session: AsyncSession):
    await callback.message.answer(text="Каталог товаров:")
    products = await ProductsRepoImpl(session=session).get_all()
    for idx, product in enumerate(products, start=1):
        await callback.answer()
        await callback.message.answer(
            f"{idx}  {product.name}\n {product.description}",
            reply_markup=types.ReplyKeyboardRemove(),
        )
