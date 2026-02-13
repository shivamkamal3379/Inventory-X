from typing import List, Optional
from sqlalchemy.orm import Session
from src.services.base import CRUDBase
from src.models.transactions import RentOutTxn, ReturnTxn
from src.models.people import Party, PartyStatus
from src.models.inventory import AvailableStock
from src.schemas.transactions import (
    RentOutTxnCreate,
    RentOutTxnBase,
    ReturnTxnCreate,
    ReturnTxnBase,
)
from fastapi import HTTPException


def _recalculate_party_status(party: Party) -> None:
    """Recalculate party status based on business rules.
    Skip if manually set to DEFAULT (manual override).
    """
    if party.status == PartyStatus.DEFAULT:
        return

    if (party.activeItems or 0) > 0:
        party.status = PartyStatus.ACTIVE
    elif (party.balance or 0) > 0:
        party.status = PartyStatus.PAYMENT_DUE
    elif party.activeItems == 0 and (party.balance or 0) <= 0:
        party.status = PartyStatus.CLOSED
    else:
        party.status = PartyStatus.INACTIVE


class CRUDRentOutTxn(CRUDBase[RentOutTxn, RentOutTxnCreate, RentOutTxnBase]):
    def create(self, db: Session, *, obj_in: RentOutTxnCreate) -> RentOutTxn:
        # --- Stock validation & update ---
        stock = (
            db.query(AvailableStock)
            .filter(AvailableStock.itemId == obj_in.itemId)
            .first()
        )
        if not stock:
            raise HTTPException(
                status_code=404, detail="Stock info not found for this item"
            )

        if stock.availableQty < obj_in.itemQty:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {stock.availableQty}, Requested: {obj_in.itemQty}",
            )

        stock.availableQty -= obj_in.itemQty
        stock.RentedOutQty += obj_in.itemQty
        db.add(stock)

        # --- Party balance & status update ---
        party = db.query(Party).filter(Party.id == obj_in.partyId).first()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")

        rent_amount = obj_in.rentAmount or 0.0
        paid_amount = obj_in.paidAmount or 0.0
        party.balance = (party.balance or 0) + rent_amount - paid_amount
        party.activeItems = (party.activeItems or 0) + obj_in.itemQty
        _recalculate_party_status(party)
        db.add(party)

        # --- Create the transaction record ---
        return super().create(db, obj_in=obj_in)

    def get_by_party(self, db: Session, *, party_id: str) -> List[RentOutTxn]:
        return db.query(self.model).filter(self.model.partyId == party_id).all()


class CRUDReturnTxn(CRUDBase[ReturnTxn, ReturnTxnCreate, ReturnTxnBase]):
    def create(self, db: Session, *, obj_in: ReturnTxnCreate) -> ReturnTxn:
        # --- Stock update ---
        stock = (
            db.query(AvailableStock)
            .filter(AvailableStock.itemId == obj_in.itemId)
            .first()
        )
        if not stock:
            raise HTTPException(
                status_code=404, detail="Stock info not found for this item"
            )

        stock.availableQty += obj_in.itemQty
        stock.RentedOutQty = max(0, stock.RentedOutQty - obj_in.itemQty)
        db.add(stock)

        # --- Party balance & status update ---
        party = db.query(Party).filter(Party.id == obj_in.partyId).first()
        if not party:
            raise HTTPException(status_code=404, detail="Party not found")

        refund = obj_in.refundAmount or 0.0
        party.balance = (party.balance or 0) - refund
        party.activeItems = max(0, (party.activeItems or 0) - obj_in.itemQty)
        _recalculate_party_status(party)
        db.add(party)

        # --- Create the transaction record ---
        return super().create(db, obj_in=obj_in)

    def get_by_party(self, db: Session, *, party_id: str) -> List[ReturnTxn]:
        return db.query(self.model).filter(self.model.partyId == party_id).all()


rentout_service = CRUDRentOutTxn(RentOutTxn)
return_service = CRUDReturnTxn(ReturnTxn)
