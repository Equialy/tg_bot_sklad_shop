from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from src.bot.schemas.cart_schema import CartSchemaBase, CartItemSchemaBase
from src.infrastructure.database.models.cart_model import Cart, CartItem
from src.infrastructure.database.models.products_model import Variant


class CartRepoImpl:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = Cart

    async def add_to_cart(self, user_id: int, variant_id: int) -> CartSchemaBase:
        # 1) Найти или создать корзину пользователя
        cart_stmt = sa.select(self.model).where(self.model.user_id == user_id)
        cart_res = await self.session.execute(cart_stmt)
        cart = cart_res.scalar_one_or_none()

        if cart is None:
            cart = Cart(user_id=user_id)
            self.session.add(cart)
            # flush, чтобы получить cart.id
            await self.session.flush()

        # 2) Найти элемент в cart_items по variant_id
        item_stmt = sa.select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.variant_id == variant_id
        )
        item_res = await self.session.execute(item_stmt)
        item = item_res.scalar_one_or_none()

        if item:
            # позиция уже в корзине — увеличиваем количество
            item.quantity += 1
        else:
            # новая позиция
            item = CartItem(cart_id=cart.id, variant_id=variant_id, quantity=1)
            self.session.add(item)

        return CartSchemaBase.model_validate(cart)

    async def get_user_cart_products(self, user_id: int) -> list[CartItemSchemaBase]:
        # Строим запрос: из cart_items через join на carts по user_id
        stmt = (
            sa.select(CartItem)
            .join(Cart, CartItem.cart_id == Cart.id)
            .where(Cart.user_id == user_id)
            # Подгружаем навигационные свойства, если они понадобятся в схемах:
            .options(
                joinedload(CartItem.cart),
                joinedload(CartItem.variant).joinedload(Variant.product),
            )
        )
        result = await self.session.execute(stmt)
        items: list[CartItem] = result.scalars().all()
        return [CartItemSchemaBase.model_validate(item) for item in items]

    async def remove_item_from_cart(
        self, user_id: int, variant_id: int
    ) -> CartItemSchemaBase | bool:
        # Сначала найдём саму корзину, чтобы получить её id
        cart_stmt = sa.select(Cart.id).where(Cart.user_id == user_id)
        cart_res = await self.session.execute(cart_stmt)
        cart_id = cart_res.scalar_one_or_none()
        if cart_id is None:
            return False

        # Удаляем нужный CartItem
        del_stmt = (
            sa.delete(CartItem)
            .where(CartItem.cart_id == cart_id, CartItem.variant_id == variant_id)
            .returning(CartItem.id)
        )
        res = await self.session.execute(del_stmt)

        # Если возвращён хотя бы один id — удаление прошло
        deleted = res.scalars().all()
        return CartItemSchemaBase.model_validate(deleted)

    async def reduce_item_quantity(self, user_id: int, variant_id: int) -> bool | None:
        """
        Уменьшает количество variant_id в корзине user_id на 1.
        Если после уменьшения количество == 0, удаляет позицию.
        Возвращает:
          - True  — позиция осталась, quantity уменьшилось
          - False — позиция удалена (количество было 1)
          - None  — позиции не было изначально
        """
        # 1) Найдём позицию в cart_items через join на carts по user_id
        stmt = (
            sa.select(CartItem)
            .join(Cart, CartItem.cart_id == Cart.id)
            .where(Cart.user_id == user_id, CartItem.variant_id == variant_id)
        )
        result = await self.session.execute(stmt)
        item: CartItem | None = result.scalar_one_or_none()
        if item is None:
            # В корзине не было такой позиции
            return None
        if item.quantity > 1:
            item.quantity -= 1
            await self.session.commit()
            return True
        else:
            # quantity == 1 — удаляем позицию
            await self.session.execute(
                sa.delete(CartItem).where(CartItem.id == item.id)
            )
            return False
