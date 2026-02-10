from src.services.base import CRUDBase
from src.models.inventory import Item, AvailableStock, RentalPrice
from sqlalchemy.orm import relationship, Session
from src.schemas.inventory import (
    ItemCreate,
    ItemBase,
    AvailableStockBase,
    RentalPriceCreate,
    RentalPriceBase,
)


class CRUDItem(CRUDBase[Item, ItemCreate, ItemBase]):
    def create(self, db: Session, *, obj_in: ItemCreate) -> Item:
        db_obj = super().create(db, obj_in=obj_in)
        # Auto-create stock entry
        stock = AvailableStock(
            itemId=db_obj.itemId,
            qty=db_obj.qty,
            availableQty=db_obj.qty,
            RentedOutQty=0,
        )
        db.add(stock)
        db.commit()
        db.refresh(db_obj)
        return db_obj


class CRUDAvailableStock(
    CRUDBase[AvailableStock, AvailableStockBase, AvailableStockBase]
):
    pass


class CRUDRentalPrice(CRUDBase[RentalPrice, RentalPriceCreate, RentalPriceBase]):
    pass


item_service = CRUDItem(Item)
stock_service = CRUDAvailableStock(AvailableStock)
price_service = CRUDRentalPrice(RentalPrice)
