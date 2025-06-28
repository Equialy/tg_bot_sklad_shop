from aiogram import Router, types, Bot, F
from aiogram.filters import Command, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.chat_types import ChatTypeFilter
from src.bot.keyboards.reply_keyboard import get_reply_keyboard
from src.infrastructure.database.repositories.products_repo import ProductsRepoImpl

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
    await message.answer(text=f"Добро пожаловать {message.from_user.username} в Slad Shop")
    await message.answer(text=f"Каталог товаров", reply_markup=get_reply_keyboard("Каталог", "Корзина"))


@user_group_router.message(Command("catalog"))
@user_group_router.message(F.text == "Каталог")
async def catalog_handler_group(message: types.Message, session: AsyncSession):
    await message.answer(text="Каталог товаров:")
    products = await ProductsRepoImpl(session=session).get_all()
    for idx, product in enumerate(products, start=1):
        await message.answer(f"{idx}  {product.name}\n {product.description}",
                             reply_markup=types.ReplyKeyboardRemove())
