from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.utils.navigate_for_pages import main_menu, catalog, products, items, carts


async def get_menu_content(
    session: AsyncSession,
    level: int,
    menu_name: str,
    product_id: int | None = None,
    category: int | None = None,
    page: int | None = None,
    user_id: int | None = None,
):

    if level == 0:
        return await main_menu(session, level, menu_name)
    elif level == 1:
        return await catalog(session, level, menu_name)
    elif level == 2:
        return await products(session, level, category)
    elif level == 3:
        return await items(
            session=session, level=level, page=page, product_id=product_id
        )
    elif level == 4:
        return await carts(session, level, menu_name, page, user_id, product_id)
