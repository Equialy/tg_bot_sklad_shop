import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.strategy import FSMStrategy

from src.bot.bot_commands.commands import private
from src.bot.handlers.admin import admin_router
from src.bot.handlers.user import user_private_router
from src.bot.handlers.user_group import user_group_router
from src.bot.middlwares.database import DatabaseSessionMiddleware
from src.config import config
from src.infrastructure.database.connection import  AsyncSessionFactory

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # redis = Redis(host=config.setting.cache.host)
    # storage = RedisStorage(redis=redis)

    bot = Bot(token=config.setting.tg_bot.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot.my_admins_list = [config.setting.tg_bot.admin_id]

    dp = Dispatcher(fsm_strategy = FSMStrategy.USER_IN_CHAT)
    dp.update.middleware(DatabaseSessionMiddleware(session_factory=AsyncSessionFactory))
    dp.include_routers(
        # echo_router,
        admin_router,
        user_private_router,
        user_group_router,

    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.get_updates(offset=-1)
        await bot.set_my_commands(commands=private, scope=types.BotCommandScopeAllPrivateChats())
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await dp.fsm.storage.close()
        await bot.session.close()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    logger.info("Bot stopped!")
