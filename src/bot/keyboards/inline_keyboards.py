from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards.reply_keyboard import get_reply_keyboard


def get_callback_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))

    return keyboard.adjust(*sizes).as_markup()


def get_url_btns(*, btns: dict[str, str], sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


ADMIN_KB = get_reply_keyboard(
    "Добавить товар",
    "Добавить категорию",
    "Каталог",
    "Изменить товар",
    placeholder="Выберите действие",
    size=(
        2,
        1,
    ),
)
ADMIN_INLINE_KB = get_callback_btns(
    btns={
        "Добавить модель": "add_product",
        # "Изменить товар модели": "update_variant",
        "Добавить категорию": "add_category",
        "Каталог моделей": "catalog_products",
        "Добавить товар по модели": "add_item_product",
        "Добавить баннер": "add_banner",
    }
)
