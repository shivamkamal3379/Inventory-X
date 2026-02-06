from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class Item(Base):
    __tablename__ = "t_Item"

    itemId = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    qty = Column(Integer, default=0)  # Master quantity
    created_at = Column(DateTime, default=func.now())
    size = Column(String(50))
    weight = Column(String(50))
    # ManufactureYr is datetime in ERD, usually just Year or Date is enough, keeping Datetime
    ManufactureYr = Column(DateTime)
    materialType = Column(String(50))
    model = Column(String(100))
    additionalParam1 = Column(String(255))

    stock = relationship("AvailableStock", back_populates="item", uselist=False)
    price = relationship("RentalPrice", back_populates="item", uselist=False)


class AvailableStock(Base):
    __tablename__ = "t_AvaiableStock"

    itemId = Column(Integer, ForeignKey("t_Item.itemId"), primary_key=True)
    # qty from Item is referenced in ERD as FK, but practically it's just linked via itemId
    # We can store a copy or just rely on Item.qty.
    # ERD says: qty number fk // reference from itemMaster // Make sure It Do Not change
    # I will not make it a db-level FK column to a non-PK column usually, unless Item.qty is unique?
    # I'll just keep it as a field for now or omit if redundant.
    # ERD has it, I'll add it but it might be redundant.
    qty = Column(Integer)
    RentedOutQty = Column(Integer, default=0)
    availableQty = Column(Integer, default=0)

    item = relationship("Item", back_populates="stock")


class RentalPrice(Base):
    __tablename__ = "RentalPrice"

    itemId = Column(Integer, ForeignKey("t_Item.itemId"), primary_key=True)
    itemName = Column(
        String(100)
    )  # Redundant if linked to item, but keeping as per ERD
    rent = Column(Float, nullable=False)
    rentFrequency = Column(String(50))  # e.g. daily, monthly

    item = relationship("Item", back_populates="price")
