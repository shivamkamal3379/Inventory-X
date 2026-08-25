from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.models.inventory import AvailableStock, Item, RentalPrice
from src.schemas.inventory import (
    ItemCreate,
    ItemUpdate,
    RentalPriceCreate,
    RentalPriceUpdate,
)
from src.services.base import CRUDBase


class CRUDItem(CRUDBase[Item, ItemCreate, ItemUpdate]):
    def create(self, db: Session, *, obj_in: ItemCreate, commit: bool = True) -> Item:
        """Create the item, its stock row and (optionally) its price atomically."""
        payload = obj_in.model_dump(exclude={"rent", "rentFrequency"})
        item = Item(**payload)
        db.add(item)
        db.flush()  # assigns itemId without ending the transaction

        db.add(
            AvailableStock(
                itemId=item.itemId,
                qty=item.qty,
                availableQty=item.qty,
                RentedOutQty=0,
            )
        )

        if obj_in.rent is not None:
            db.add(
                RentalPrice(
                    itemId=item.itemId,
                    itemName=item.name,
                    rent=obj_in.rent,
                    rentFrequency=obj_in.rentFrequency,
                )
            )

        if commit:
            db.commit()
            db.refresh(item)
        return item

    def update(
        self, db: Session, *, db_obj: Item, obj_in: ItemUpdate | dict, commit: bool = True
    ) -> Item:
        """Update the item and keep its stock row consistent.

        Changing the master qty has to be reflected in AvailableStock, otherwise
        the two drift apart and the check constraint
        (availableQty + RentedOutQty = qty) is violated on the next write.
        """
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        new_qty = update_data.get("qty")

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)

        if new_qty is not None:
            stock = db.get(AvailableStock, db_obj.itemId, with_for_update=True)
            if stock is None:
                stock = AvailableStock(
                    itemId=db_obj.itemId, qty=new_qty, availableQty=new_qty, RentedOutQty=0
                )
                db.add(stock)
            else:
                if new_qty < stock.RentedOutQty:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"Cannot reduce quantity to {new_qty}: "
                            f"{stock.RentedOutQty} unit(s) are currently rented out."
                        ),
                    )
                stock.qty = new_qty
                stock.availableQty = new_qty - stock.RentedOutQty
                db.add(stock)

        # Keep the denormalised price label in step with a renamed item.
        if "name" in update_data:
            price = db.get(RentalPrice, db_obj.itemId)
            if price is not None:
                price.itemName = update_data["name"]
                db.add(price)

        if commit:
            db.commit()
            db.refresh(db_obj)
        else:
            db.flush()
        return db_obj

    def list_with_stock(
        self, db: Session, *, q: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[dict]:
        """One query returning item + stock + price, instead of N+1 per row."""
        stmt = (
            select(Item, AvailableStock, RentalPrice)
            .outerjoin(AvailableStock, AvailableStock.itemId == Item.itemId)
            .outerjoin(RentalPrice, RentalPrice.itemId == Item.itemId)
        )
        if q:
            term = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Item.name).like(term),
                    func.lower(func.coalesce(Item.description, "")).like(term),
                )
            )
        stmt = stmt.order_by(Item.itemId.desc()).offset(skip).limit(limit)

        rows = []
        for item, stock, price in db.execute(stmt).all():
            rows.append(
                {
                    **{c.name: getattr(item, c.name) for c in item.__table__.columns},
                    "availableQty": stock.availableQty if stock else 0,
                    "rentedOutQty": stock.RentedOutQty if stock else 0,
                    "rent": price.rent if price else None,
                    "rentFrequency": price.rentFrequency if price else None,
                }
            )
        return rows


class CRUDRentalPrice(CRUDBase[RentalPrice, RentalPriceCreate, RentalPriceUpdate]):
    def create(self, db: Session, *, obj_in: RentalPriceCreate, commit: bool = True) -> RentalPrice:
        # SQLite would happily accept a price for a nonexistent item without the
        # FK pragma; check explicitly so both backends behave identically.
        if db.get(Item, obj_in.itemId) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {obj_in.itemId} does not exist.",
            )
        return super().create(db, obj_in=obj_in, commit=commit)


item_service = CRUDItem(Item)
price_service = CRUDRentalPrice(RentalPrice)


def get_stock(db: Session, item_id: int) -> AvailableStock | None:
    return db.get(AvailableStock, item_id)
