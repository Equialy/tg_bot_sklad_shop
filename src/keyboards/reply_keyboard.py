from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def get_reply_keyboard(
        *btns: str,
        placeholder: str =None,
        contacts: int = None,
        location: int = None,
        size: tuple[int,...] = (2,),

) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    for idx, text in enumerate(btns, start=0):
        if contacts and contacts == idx:
            builder.button(text=text)
        if location and location == idx:
            builder.button(text=text)
        else:
            builder.button(text=text)
    return builder.adjust(*size).as_markup(resize_keyboard= True,input_field_placeholder=placeholder)

