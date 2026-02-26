from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ItemBase(BaseModel):
    name: str 
    description: Optional[str] = None
    qty: int = 0
    size: Optional[str] = None
    weight: Optional[str] = None
    manufactureYr: Optional[datetime] = None
    materialType: Optional[str] = None
    model: Optional[str] = None
    additionalParam1: Optional[str] = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(ItemBase):
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    pass


class ItemOut(ItemBase):
    itemId: int

    created_at: datetime = Field(default_factory=lambda: datetime.now())

    class Config:
        from_attributes = True


class AvailableStockBase(BaseModel):
    qty: Optional[int] = 0
    RentedOutQty: Optional[int] = 0
    availableQty: Optional[int] = 0


class AvailableStockOut(AvailableStockBase):
    itemId: int
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    class Config:
        from_attributes = True


class RentalPriceBase(BaseModel):
    itemName: Optional[str] = None
    rent: float
    rentFrequency: Optional[str] = None


class RentalPriceCreate(RentalPriceBase):
    itemId: int


class RentalPriceOut(RentalPriceBase):
    itemId: int
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    class Config:
        from_attributes = True
        