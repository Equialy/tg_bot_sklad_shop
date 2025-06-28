from aiogram import Router, types, Bot
from aiogram.filters import CommandStart, Command

from src.filters.chat_types import ChatTypeFilter

user_group_router = Router(name=__name__)
user_group_router.message.filter(ChatTypeFilter(["group", "supergroup"]))

restricted = {"хомяк"}





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

# @user_group_router.message(CommandStart())
# async def clean_text(message: types.Message):
#     if restricted.intersection(message.text.lower().split()):
#         await message.answer(text="Соблюдайте порядок")
#         await message.delete()
