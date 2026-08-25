from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class Item(Base):
    __tablename__ = "t_Item"
    __table_args__ = (CheckConstraint("qty >= 0", name="ck_item_qty_non_negative"),)

    itemId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    size: Mapped[str | None] = mapped_column(String(50))
    weight: Mapped[str | None] = mapped_column(String(50))
    # Named to match the API contract exactly. The previous mismatch between the
    # schema field (manufactureYr) and this column (ManufactureYr) made every
    # POST /items/ raise TypeError before it reached the database.
    manufactureYr: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    materialType: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(100))
    additionalParam1: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    stock: Mapped["AvailableStock | None"] = relationship(
        back_populates="item",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    price: Mapped["RentalPrice | None"] = relationship(
        back_populates="item",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AvailableStock(Base):
    __tablename__ = "t_AvaiableStock"
    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_stock_qty_non_negative"),
        CheckConstraint('"RentedOutQty" >= 0', name="ck_stock_rented_non_negative"),
        CheckConstraint('"availableQty" >= 0', name="ck_stock_available_non_negative"),
        # The invariant the whole rental flow depends on: nothing is ever lost or
        # conjured. Enforced by the database, not only by application code.
        CheckConstraint(
            '"availableQty" + "RentedOutQty" = qty',
            name="ck_stock_conservation",
        ),
    )

    itemId: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_Item.itemId", ondelete="CASCADE"), primary_key=True
    )
    qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    RentedOutQty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    availableQty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    item: Mapped["Item"] = relationship(back_populates="stock")


class RentalPrice(Base):
    __tablename__ = "RentalPrice"
    __table_args__ = (CheckConstraint("rent >= 0", name="ck_price_rent_non_negative"),)

    itemId: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_Item.itemId", ondelete="CASCADE"), primary_key=True
    )
    itemName: Mapped[str | None] = mapped_column(String(100))
    rent: Mapped[float] = mapped_column(Float, nullable=False)
    rentFrequency: Mapped[str | None] = mapped_column(String(50))
    updated_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    item: Mapped["Item"] = relationship(back_populates="price")
