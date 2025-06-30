from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command, or_f
from aiogram.types import InputMediaPhoto
from aiogram.utils import markdown
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter
from src.bot.keyboards.inline_common_buttons import get_callback_btns, get_url_btns
from src.bot.keyboards.inline_keyboards import MenuCallBack
from src.bot.keyboards.menu import get_menu_content
from src.bot.schemas.user_schema import UserSchemaRead
from src.bot.utils.payment import create, check_payment
from src.config.config import setting
from src.infrastructure.database.repositories.banner_repo import BannerRepoImpl
from src.infrastructure.database.repositories.cart_repo import CartRepoImpl
from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl
from src.infrastructure.database.repositories.user_repo import UserRepoImpl
from src.infrastructure.database.repositories.variant_repo import VariantRepositoryImpl

user_private_router = Router(name=__name__)
user_private_router.message.filter(ChatTypeFilter(["private"]))


@user_private_router.message(CommandStart())
async def start_handler(message: types.Message, session: AsyncSession):
    media, reply_markup = await get_menu_content(session, level=0, menu_name="main")

    await message.answer_photo(
        media.media, caption=media.caption, reply_markup=reply_markup
    )


async def add_to_cart(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):
    user = callback.from_user
    await CartRepoImpl(session=session).add_to_cart(
        user_telegram_id=user.id, variant_id=callback_data.item_id
    )
    await callback.answer(text="Товар добавлен в корзину.", show_alert=True)


@user_private_router.callback_query(MenuCallBack.filter())
async def user_menu(
    callback: types.CallbackQuery, callback_data: MenuCallBack, session: AsyncSession
):

    if callback_data.menu_name == "add_to_cart":
        await add_to_cart(callback, callback_data, session)
        return
    media, reply_markup = await get_menu_content(
        session,
        level=callback_data.level,
        menu_name=callback_data.menu_name,
        category=callback_data.category,
        page=callback_data.page,
        product_id=callback_data.product_id,
        user_id=callback.from_user.id,
        item_id=callback_data.item_id,
        username=callback_data.username,
    )

    await callback.message.edit_media(media=media, reply_markup=reply_markup)
    await callback.answer()


@user_private_router.callback_query(F.data == "buy")
async def payment_handler(callback: types.CallbackQuery, session: AsyncSession):
    payment_url, payment_id = await create(
        amount=setting.payment.price, telegram_id=callback.from_user.id
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="Оплатить", url=f"{payment_url}")
    builder.button(text="Проверить оплату", callback_data=f"check_{payment_id}")

    await callback.message.answer(
        text=f"Оплата через Юкасса" f"{payment_url} " f"\nID платежа: {payment_id}",
        reply_markup=builder.as_markup(),
    )


@user_private_router.callback_query(F.data.startswith("check"))
async def check_handler(callback: types.CallbackQuery, session: AsyncSession):
    result = await check_payment(payment_id=callback.data.split("_")[-1])
    if result:
        await callback.message.answer(text="Оплата еще не прошла")

    else:
        await callback.message.answer(text="Оплата прошла успешно")
    await callback.answer()


#
# @user_private_router.message(CommandStart())
# async def start_handler(message: types.Message, session: AsyncSession):
#     main_photo = await BannerRepoImpl(session=session).get_banner(page="main")
#     await message.answer_photo(
#         photo=main_photo.image,
#         text=main_photo.description,
#         reply_markup=get_callback_btns(btns={"Каталог": "catalog", "Корзина": "carts"}),
#     )
#
#
# @user_private_router.callback_query(F.data == "catalog")
# async def categories_products(callback: types.CallbackQuery, session: AsyncSession):
#     await callback.answer()
#     categories = await CategoryRepositoryImpl(session=session).get_all()
#     catalog_photo = await BannerRepoImpl(session=session).get_banner(page=callback.data)
#     media = InputMediaPhoto(
#         media=catalog_photo.image,
#         caption=catalog_photo.description,
#     )
#     btns = {f"{cat.name}": f"category_id_{cat.id}" for cat in categories}
#     await callback.message.edit_media(
#         media=media,
#         reply_markup=get_callback_btns(btns=btns),
#     )
#
#
# @user_private_router.callback_query(F.data.startswith("category_id_"))
# async def get_products_by_category(
#     callback: types.CallbackQuery, session: AsyncSession
# ):
#     await callback.answer()
#     products = await ProductsRepoImpl(session=session).get_by_category(
#         int(callback.data.split("_")[-1])
#     )
#     media_photo = await BannerRepoImpl(session=session).get_banner(
#         page=callback.data.split("_")[0]
#     )
#     media = InputMediaPhoto(
#         media=media_photo.image,
#         text=media_photo.description,
#         caption=media_photo.description,
#     )
#     btns = {
#         f"{product.name}": f"product_id_for_item_{product.id}" for product in products
#     }
#     btns["⬅ Назад"] = "catalog"
#     await callback.message.edit_media(
#         media=media,
#         text="Товары",
#         reply_markup=get_callback_btns(btns=btns),
#     )
#
#
# @user_private_router.callback_query(F.data.startswith("product_id_for_item_"))
# async def get_info_by_product(callback: types.CallbackQuery, session: AsyncSession):
#     await callback.answer()
#     info_item = await VariantRepositoryImpl(session=session).get_by_id_product(
#         product_id=int(callback.data.split("_")[-1])
#     )
#     for item in info_item:
#         media = InputMediaPhoto(
#             media=item.photo1,
#             caption=f"Товары по данной модели: \n"
#             f"Описание: \n{markdown.hbold(item.description)}\n"
#             f"Цена: {markdown.hbold(item.price)}\n"
#             f"В наличии: {markdown.hbold(item.stock)}\n"
#             f"Sku: {markdown.hbold(item.sku)}\n"
#             f"ID product: {markdown.hbold(item.product_id)}\n",
#         )
#
#         await callback.message.edit_media(
#             media=media,
#             reply_markup=get_callback_btns(
#                 btns={
#                     "Добавить в корзину": f"add_to_cart_{item.id}",
#                     "⬅ Каталог": f"catalog",
#                 }
#             ),
#         )
#
#
# @user_private_router.callback_query(F.data.startswith("add_to_cart_"))
# async def add_to_cart(callback: types.CallbackQuery, session: AsyncSession):
#     await callback.answer()
#     add_cart = await CartRepoImpl(session=session).add_to_cart(
#         user_id=callback.from_user.id,
#         variant_id=int(callback.data.split("_")[-1]),
#         username=callback.from_user.username,
#     )
#     await callback.answer(text="Товар добавлен в корзину", show_alert=True)
#
#
# @user_private_router.callback_query(
#     or_f(Command("catalog"), (F.data.startswith("catalog")))
# )
# async def catalog_handler_group(callback: types.CallbackQuery, session: AsyncSession):
#     await callback.message.answer(text="Каталог товаров:")
#     products = await ProductsRepoImpl(session=session).get_all()
#     for idx, product in enumerate(products, start=1):
#         await callback.answer()
#         await callback.message.answer(
#             f"{idx}  {product.name}\n {product.description}",
#             reply_markup=types.ReplyKeyboardRemove(),
#         )
