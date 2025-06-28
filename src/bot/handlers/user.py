from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl

user_private_router = Router(name=__name__)
user_private_router.message.filter(ChatTypeFilter(["private"]))

# @user_private_router.message(CommandStart())
# async def start_handler(message: types.Message):
#     await message.answer(text=f"Добро пожаловать {message.from_user.username} в Slad Shop")
#     await message.answer(text=f"Каталог товаров", reply_markup=get_reply_keyboard("Каталог", "Корзина"))
#
#
