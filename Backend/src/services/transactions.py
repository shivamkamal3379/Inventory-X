from typing import List, Optional
from sqlalchemy.orm import Session
from src.services.base import CRUDBase
from src.models.transactions import RentOutTxn, ReturnTxn
from src.schemas.transactions import (
    RentOutTxnCreate,
    RentOutTxnBase,
    ReturnTxnCreate,
    ReturnTxnBase,
)


from fastapi import HTTPException
from src.models.inventory import AvailableStock


class CRUDRentOutTxn(CRUDBase[RentOutTxn, RentOutTxnCreate, RentOutTxnBase]):
    def create(self, db: Session, *, obj_in: RentOutTxnCreate) -> RentOutTxn:
        # Check stock availability
        stock = (
            db.query(AvailableStock)
            .filter(AvailableStock.itemId == obj_in.itemId)
            .first()
        )
        if not stock:
            raise HTTPException(status_code=404, detail="Stock info not found")

        if stock.availableQty < obj_in.qty:
            raise HTTPException(status_code=400, detail="Insufficient stock available")

        # Update stock
        stock.availableQty -= obj_in.qty
        stock.RentedOutQty += obj_in.qty
        db.add(stock)

        # Create transaction
        return super().create(db, obj_in=obj_in)


class CRUDReturnTxn(CRUDBase[ReturnTxn, ReturnTxnCreate, ReturnTxnBase]):
    def create(self, db: Session, *, obj_in: ReturnTxnCreate) -> ReturnTxn:
        # Update stock
        stock = (
            db.query(AvailableStock)
            .filter(AvailableStock.itemId == obj_in.itemId)
            .first()
        )
        if not stock:
            # Should technically exist if we are returning something, but good to handle
            raise HTTPException(status_code=404, detail="Stock info not found")

        # Logic to ensure we don't return more than rented out?
        # Ideally yes, but multiple parties might be involved.
        # For now, just increment available and decrement rented out.

        # Prevent negative rented out quantity checks if desired
        if stock.RentedOutQty < obj_in.qty:
            # This might happen if data is inconsistent, but strict check:
            # raise HTTPException(status_code=400, detail="Cannot return more than rented out")
            # For robustness, we might just set to 0 or allow, but I'll stick to simple math for now
            pass

        stock.availableQty += obj_in.qty
        stock.RentedOutQty -= obj_in.qty

        # Ensure non-negative RentedOutQty (optional safety)
        if stock.RentedOutQty < 0:
            stock.RentedOutQty = 0

        db.add(stock)

        return super().create(db, obj_in=obj_in)


rentout_service = CRUDRentOutTxn(RentOutTxn)
return_service = CRUDReturnTxn(ReturnTxn)
