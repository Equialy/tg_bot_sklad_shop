from datetime import date, datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, CheckConstraint, Text, Numeric, ForeignKey, Integer
from sqlalchemy import DateTime, func

from src.infrastructure.database.connection import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    variants: Mapped[list["Variant"]] = relationship(
        "Variant", back_populates="product", cascade="all, delete-orphan"
    )

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    parent: Mapped["Category" ] = relationship(
        "Category", back_populates="children", remote_side=[id]
    )
    children: Mapped[list["Category"]] = relationship(
        "Category", back_populates="parent", cascade="all"
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )

class Variant(Base):
    __tablename__ = "variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
    )
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    price: Mapped[Numeric] = mapped_column(Numeric(18, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo1: Mapped[str | None] = mapped_column(String, nullable=True)
    photo2: Mapped[str | None] = mapped_column(String, nullable=True)

    product: Mapped[Product] = relationship("Product", back_populates="variants")
