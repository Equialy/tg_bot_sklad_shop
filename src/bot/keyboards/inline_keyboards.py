from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.schemas.product_schema import ProductSchemaBase


class MenuCallBack(CallbackData, prefix="menu"):
    level: int
    menu_name: str
    category: int | None = None
    page: int = 1
    product_id: int | None = None
    item_id: int | None = None


def get_user_main_btns(*, level: int, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    btns = {
        "Каталог 🛍": "catalog",
        "Корзина 🛒": "carts",
        "О нас ℹ️": "about",
        "Оплата 💰": "payment",
        "Доставка ⛵": "shipping",
    }
    for text, menu_name in btns.items():
        if menu_name == "catalog":
            keyboard.button(
                text=text,
                callback_data=MenuCallBack(level=level + 1, menu_name=menu_name).pack(),
            )
        elif menu_name == "cart":
            keyboard.button(
                text=text,
                callback_data=MenuCallBack(level=4, menu_name=menu_name).pack(),
            )
        else:
            keyboard.button(
                text=text,
                callback_data=MenuCallBack(level=level, menu_name=menu_name).pack(),
            )

    return keyboard.adjust(*sizes).as_markup()


def get_user_catalog_btns(*, level: int, categories: list, sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Назад",
        callback_data=MenuCallBack(level=level - 1, menu_name="main").pack(),
    )
    keyboard.button(
        text="Корзина 🛒",
        callback_data=MenuCallBack(level=3, menu_name="carts").pack(),
    )
    for c in categories:
        keyboard.button(
            text=c.name,
            callback_data=MenuCallBack(
                level=level + 1, menu_name=c.name, category=c.id
            ).pack(),
        )

    return keyboard.adjust(*sizes).as_markup()


def get_products_models_btns(
    *, level: int, product_id: list[ProductSchemaBase], sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="Назад",
        callback_data=MenuCallBack(level=level - 1, menu_name="catalog").pack(),
    )
    keyboard.button(
        text="Корзина 🛒", callback_data=MenuCallBack(level=3, menu_name="carts").pack()
    )
    for p in product_id:
        keyboard.button(
            text=p.name,
            callback_data=MenuCallBack(
                level=level + 1, menu_name=p.name, product_id=p.id
            ).pack(),
        )
    return keyboard.adjust(*sizes).as_markup()


def get_items_btns(
    level, item_id, page, product_id: int, pagination_btns, sizes: tuple[int] = (2, 1)
):
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="Назад в каталог",
        callback_data=MenuCallBack(level=level - 2, menu_name="catalog").pack(),
    )
    keyboard.button(
        text="Корзина 🛒", callback_data=MenuCallBack(level=3, menu_name="cart").pack()
    )
    keyboard.button(
        text="Купить 💵",
        callback_data=MenuCallBack(
            level=level, menu_name="add_to_cart", item_id=item_id
        ).pack(),
    )

    keyboard.adjust(*sizes)

    row = []
    for text, menu_name in pagination_btns.items():
        if menu_name == "next":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        product_id=product_id,
                        item_id=item_id,
                        page=page + 1,
                    ).pack(),
                )
            )

        elif menu_name == "previous":
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=MenuCallBack(
                        level=level,
                        menu_name=menu_name,
                        product_id=product_id,
                        item_id=item_id,
                        page=page - 1,
                    ).pack(),
                )
            )

    return keyboard.row(*row).as_markup()


def get_user_cart(
    *,
    level: int,
    page: int | None,
    pagination_btns: dict | None,
    item_id: int | None,
    sizes: tuple[int] = (3,)
):
    keyboard = InlineKeyboardBuilder()
    if page:
        keyboard.button(
            text="Удалить",
            callback_data=MenuCallBack(
                level=level, menu_name="delete", item_id=item_id, page=page
            ).pack(),
        )
        keyboard.button(
            text="-1",
            callback_data=MenuCallBack(
                level=level, menu_name="decrement", item_id=item_id, page=page
            ).pack(),
        )
        keyboard.button(
            text="+1",
            callback_data=MenuCallBack(
                level=level, menu_name="increment", item_id=item_id, page=page
            ).pack(),
        )

        keyboard.adjust(*sizes)

        row = []
        for text, menu_name in pagination_btns.items():
            if menu_name == "next":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallBack(
                            level=level, menu_name=menu_name, page=page + 1
                        ).pack(),
                    )
                )
            elif menu_name == "previous":
                row.append(
                    InlineKeyboardButton(
                        text=text,
                        callback_data=MenuCallBack(
                            level=level, menu_name=menu_name, page=page - 1
                        ).pack(),
                    )
                )

        keyboard.row(*row)

        row2 = [
            InlineKeyboardButton(
                text="На главную 🏠",
                callback_data=MenuCallBack(level=0, menu_name="main").pack(),
            ),
            InlineKeyboardButton(
                text="Заказать",
                callback_data=MenuCallBack(level=0, menu_name="order").pack(),
            ),
        ]
        return keyboard.row(*row2).as_markup()
    else:
        keyboard.add(
            InlineKeyboardButton(
                text="На главную 🏠",
                callback_data=MenuCallBack(level=0, menu_name="main").pack(),
            )
        )

        return keyboard.adjust(*sizes).as_markup()
