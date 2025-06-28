from aiogram import Router, Bot
from aiogram.filters import Filter
from aiogram.types import Message



class ChatTypeFilter(Filter):
    def __init__(self, chat_type: list[str]) -> None:
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_type

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, bot: Bot) -> bool:
        return message.from_user.id in bot.my_admins_list
