from aiogram import Router, types
from aiogram.filters import CommandStart, Command

user_private_router = Router(name=__name__)

@user_private_router.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer(text=f"Добро пожаловать {message.from_user.username} в Slad Shop")

@user_private_router.message(Command("catalog"))
async def catalog_handler(messsage: types.Message):
    await messsage.answer(text="Каталог товаров:")