from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    qty: int = Field(default=0, ge=0)
    size: str | None = Field(default=None, max_length=50)
    weight: str | None = Field(default=None, max_length=50)
    manufactureYr: datetime | None = None
    materialType: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=100)
    additionalParam1: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    """Optionally sets the rental price in the same call.

    The documented API (README §2) posts `rent` alongside the item, so both are
    accepted here and the RentalPrice row is created in the same transaction.
    """

    rent: float | None = Field(default=None, ge=0)
    rentFrequency: str | None = Field(default=None, max_length=50)


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    qty: int | None = Field(default=None, ge=0)
    size: str | None = Field(default=None, max_length=50)
    weight: str | None = Field(default=None, max_length=50)
    manufactureYr: datetime | None = None
    materialType: str | None = Field(default=None, max_length=50)
    model: str | None = Field(default=None, max_length=100)
    additionalParam1: str | None = Field(default=None, max_length=255)


class ItemOut(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    itemId: int
    created_at: datetime | None = None


class StockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    itemId: int
    qty: int
    RentedOutQty: int
    availableQty: int


class ItemWithStockOut(ItemOut):
    """Item plus its live stock and price.

    The inventory table needs all three together; returning them in one payload
    avoids the N+1 round-trips the frontend would otherwise make per row.
    """

    availableQty: int = 0
    rentedOutQty: int = 0
    rent: float | None = None
    rentFrequency: str | None = None


class RentalPriceBase(BaseModel):
    itemName: str | None = Field(default=None, max_length=100)
    rent: float = Field(ge=0)
    rentFrequency: str | None = Field(default=None, max_length=50)


class RentalPriceCreate(RentalPriceBase):
    itemId: int


class RentalPriceUpdate(BaseModel):
    itemName: str | None = Field(default=None, max_length=100)
    rent: float | None = Field(default=None, ge=0)
    rentFrequency: str | None = Field(default=None, max_length=50)


class RentalPriceOut(RentalPriceBase):
    model_config = ConfigDict(from_attributes=True)

    itemId: int


class StockAdjust(BaseModel):
    """Absolute new master quantity for an item.

    Cannot go below what is currently rented out — that would break the
    availableQty + RentedOutQty = qty invariant.
    """

    qty: int = Field(ge=0)
