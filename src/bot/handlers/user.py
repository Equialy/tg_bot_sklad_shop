from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InputMediaPhoto
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter
from src.bot.keyboards.inline_keyboards import get_callback_btns
from src.infrastructure.database.repositories.banner_repo import BannerRepoImpl
from src.infrastructure.database.repositories.cart_repo import CartRepoImpl
from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl
from src.infrastructure.database.repositories.variant_repo import VariantRepositoryImpl

user_private_router = Router(name=__name__)
user_private_router.message.filter(ChatTypeFilter(["private"]))


# @user_private_router.message(CommandStart())
# async def start_handler(message: types.Message, session: AsyncSession): ...


@user_private_router.message(CommandStart())
async def start_handler(message: types.Message, session: AsyncSession):
    main_photo = await BannerRepoImpl(session=session).get_banner(page="main")
    await message.answer_photo(
        photo=main_photo.image,
        text=main_photo.description,
        reply_markup=get_callback_btns(btns={"Каталог": "catalog", "Корзина": "carts"}),
    )


@user_private_router.callback_query(F.data == "catalog")
async def categories_products(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    categories = await CategoryRepositoryImpl(session=session).get_all()
    catalog_photo = await BannerRepoImpl(session=session).get_banner(page=callback.data)
    media = InputMediaPhoto(
        media=catalog_photo.image,
        caption=catalog_photo.description,
    )
    btns = {f"{cat.name}": f"category_id_{cat.id}" for cat in categories}
    await callback.message.edit_media(
        media=media,
        reply_markup=get_callback_btns(btns=btns),
    )


@user_private_router.callback_query(F.data.startswith("category_id_"))
async def get_products_by_category(
    callback: types.CallbackQuery, session: AsyncSession
):
    await callback.answer()
    products = await ProductsRepoImpl(session=session).get_by_category(
        int(callback.data.split("_")[-1])
    )
    media_photo = await BannerRepoImpl(session=session).get_banner(
        page=callback.data.split("_")[0]
    )
    media = InputMediaPhoto(
        media=media_photo.image,
        text=media_photo.description,
        caption=media_photo.description,
    )
    btns = {
        f"{product.name}": f"product_id_for_item_{product.id}" for product in products
    }
    btns["⬅ Назад"] = "catalog"
    await callback.message.edit_media(
        media=media,
        text="Товары",
        reply_markup=get_callback_btns(btns=btns),
    )


@user_private_router.callback_query(F.data.startswith("product_id_for_item_"))
async def get_info_by_product(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    info_item = await VariantRepositoryImpl(session=session).get_by_id_product(
        product_id=int(callback.data.split("_")[-1])
    )
    for item in info_item:
        media = InputMediaPhoto(
            media=item.photo1,
            caption=f"Товары по данной модели: \n"
            f"Описание: \n{markdown.hbold(item.description)}\n"
            f"Цена: {markdown.hbold(item.price)}\n"
            f"В наличии: {markdown.hbold(item.stock)}\n"
            f"Sku: {markdown.hbold(item.sku)}\n"
            f"ID product: {markdown.hbold(item.product_id)}\n",
        )

        await callback.message.edit_media(
            media=media,
            reply_markup=get_callback_btns(
                btns={
                    "Добавить в корзину": f"add_to_cart_{item.id}",
                    "⬅ Каталог": f"catalog",
                }
            ),
        )


@user_private_router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: types.CallbackQuery, session: AsyncSession):
    await callback.answer()
    add_cart = await CartRepoImpl(session=session).add_to_cart(
        user_id=callback.from_user.id,
        variant_id=int(callback.data.split("_")[-1]),
        username=callback.from_user.username,
    )
    await callback.answer(text="Товар добавлен в корзину", show_alert=True)


@user_private_router.callback_query(
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
