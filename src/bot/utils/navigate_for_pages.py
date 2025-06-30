from aiogram.types import InputMediaPhoto

from src.bot.keyboards.inline_keyboards import get_user_main_btns
from src.infrastructure.database.repositories.banner_repo import BannerRepoImpl


async def main_menu(session, level, menu_name):
    banner = await BannerRepoImpl(session=session).get_banner(page=menu_name)
    image = InputMediaPhoto(media=banner.image, caption=banner.description)

    kbds = get_user_main_btns(level=level)

    return image, kbds
