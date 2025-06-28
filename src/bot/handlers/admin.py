from aiogram import Router, types
from aiogram.filters import CommandStart, Command

from src.filters.chat_types import ChatTypeFilter, IsAdmin
from src.keyboards.reply_keyboard import get_reply_keyboard

admin_router = Router(name=__name__)
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())


ADMIN_KB = get_reply_keyboard(
    "Добавить товар",
    "Изменить товар",
    "Удалить товар",
    "Я так, просто посмотреть зашел",
    placeholder="Выберите действие",
    size=(2, 1, 1),
)


@admin_router.message(Command("admin"))
async def admin_features(message: types.Message):
    await message.answer("Что хотите сделать?", reply_markup=ADMIN_KB)
