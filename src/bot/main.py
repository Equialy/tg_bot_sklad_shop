import asyncio
import logging

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, types

from src.bot.bot_commands.commands import private
from src.config import config

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )

    # redis = Redis(host=config.setting.cache.host)
    # storage = RedisStorage(redis=redis)

    bot = Bot(token=config.setting.tg_bot.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    bot.my_admins_list = []
    dp = Dispatcher()
    # dp.update.middleware(DatabaseSessionMiddleware(session_pool=AsyncSessionFactory))
    # dp.include_routers(  )

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
