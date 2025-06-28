import logging

from aiogram import Router, Bot
from aiogram.filters import Filter
from aiogram.types import Message

logger = logging.getLogger(__name__)

class ChatTypeFilter(Filter):
    def __init__(self, chat_type: list[str]) -> None:
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_type

class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: Message, bot: Bot) -> bool:
        logger.info("IsAdmin check for %s, current list: %s",
                    message.from_user.id, bot.my_admins_list)
        return message.from_user.id in bot.my_admins_list
