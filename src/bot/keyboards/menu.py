from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.navigate_for_pages import main_menu


async def get_menu_content(session: AsyncSession, level: int, menu_name: str):

    if level == 0:
        return await main_menu(session, level, menu_name)
    # elif level == 1:
    #     return await catalog(session, level, menu_name)
    # elif level == 2:
    #     return await products(session, level, category, page)
    # elif level == 3:
    #     return await carts(session, level, menu_name, page, user_id, product_id)
