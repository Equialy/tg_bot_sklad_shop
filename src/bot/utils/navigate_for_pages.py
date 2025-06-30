from aiogram.types import InputMediaPhoto

from src.bot.keyboards.inline_keyboards import (
    get_user_main_btns,
    get_user_catalog_btns,
    get_products_models_btns,
    get_items_btns,
    get_user_cart,
)
from src.bot.schemas.product_schema import ProductSchemaBase
from src.bot.schemas.variant_schema import VariantSchemaBase
from src.bot.utils.paginate import Paginator
from src.infrastructure.database.repositories.banner_repo import BannerRepoImpl
from src.infrastructure.database.repositories.cart_repo import CartRepoImpl
from src.infrastructure.database.repositories.categories_repo import (
    CategoryRepositoryImpl,
)
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl
from src.infrastructure.database.repositories.variant_repo import VariantRepositoryImpl


async def main_menu(session, level, menu_name):
    banner = await BannerRepoImpl(session=session).get_banner(page=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds


async def catalog(session, level, menu_name):
    banner = await BannerRepoImpl(session=session).get_banner(menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    categories = await CategoryRepositoryImpl(session=session).get_all()
    kbds = get_user_catalog_btns(level=level, categories=categories)

    return image, kbds


def pages(paginator: Paginator):
    btns = dict()
    if paginator.has_previous():
        btns["◀ Пред."] = "previous"

    if paginator.has_next():
        btns["След. ▶"] = "next"

    return btns


async def products(
    session,
    level,
    category,
):
    banner = await BannerRepoImpl(session=session).get_banner(page="products")
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    products: list[ProductSchemaBase] = await ProductsRepoImpl(
        session=session
    ).get_by_category(category_id=category)
    kbds = get_products_models_btns(
        level=level,
        product_id=products,
    )
    return image, kbds


async def items(session, level, product_id, page):
    items: list[VariantSchemaBase] = await VariantRepositoryImpl(
        session=session
    ).get_by_id_product(product_id=product_id)
    paginator = Paginator(items, page=page)
    page_items = paginator.get_page()
    if not page_items:
        raise IndexError(
            f"Нет товаров на странице {paginator.page} из {paginator.pages}"
        )
    product = paginator.get_page()[0]

    image = InputMediaPhoto(
        media=product.photo1,
        caption=f"<strong>{product.stock}</strong>"
        f"\n{product.description}"
        f"\nСтоимость: {round(product.price, 2)}"
        f"\n<strong>Товар {paginator.page} из {paginator.pages}</strong>",
    )

    pagination_btns = pages(paginator)

    kbds = get_items_btns(
        level=level,
        item_id=product.id,
        page=page,
        product_id=product_id,
        pagination_btns=pagination_btns,
    )

    return image, kbds


async def carts(session, level, menu_name, page, user_id, item_id):
    if menu_name == "delete":
        await CartRepoImpl(session=session).remove_item_from_cart(
            user_id, variant_id=item_id
        )
        if page > 1:
            page -= 1
    elif menu_name == "decrement":
        is_cart = await CartRepoImpl(session=session).reduce_item_quantity(
            user_id=user_id, variant_id=item_id
        )
        if page > 1 and not is_cart:
            page -= 1
    elif menu_name == "increment":
        await CartRepoImpl(session=session).add_to_cart(user_id, variant_id=item_id)

    carts = await CartRepoImpl(session=session).get_user_cart_products(user_id)

    if not carts:
        banner = await BannerRepoImpl(session=session).get_banner("cart")
        image = InputMediaPhoto(
            media=banner.image, caption=f"<strong>{banner.description}</strong>"
        )

        kbds = get_user_cart(
            level=level,
            page=None,
            pagination_btns=None,
            item_id=None,
        )

    else:
        paginator = Paginator(carts, page=page)

        cart = paginator.get_page()[0]

        cart_price = round(cart.quantity * cart.product.price, 2)
        total_price = round(
            sum(cart.quantity * cart.product.price for cart in carts), 2
        )
        image = InputMediaPhoto(
            media=cart.product.image,
            caption=f"<strong>{cart.product.name}</strong>\n{cart.product.price}$ x {cart.quantity} = {cart_price}$\
                    \nТовар {paginator.page} из {paginator.pages} в корзине.\nОбщая стоимость товаров в корзине {total_price}",
        )

        pagination_btns = pages(paginator)

        kbds = get_user_cart(
            level=level,
            page=page,
            pagination_btns=pagination_btns,
            product_id=cart.product.id,
        )

    return image, kbds
