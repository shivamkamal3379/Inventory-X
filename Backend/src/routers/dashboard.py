from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.core.database import get_db
from src.models.inventory import Item, AvailableStock
from src.models.people import Party, PartyStatus
from src.models.transactions import RentOutTxn, ReturnTxn
from pydantic import BaseModel


class DashboardStats(BaseModel):
    totalItems: int = 0
    totalParties: int = 0
    activeParties: int = 0
    totalRentedOutQty: int = 0
    totalAvailableQty: int = 0
    totalRentals: int = 0
    totalReturns: int = 0


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_items = db.query(func.count(Item.itemId)).scalar() or 0
    total_parties = db.query(func.count(Party.id)).scalar() or 0
    active_parties = (
        db.query(func.count(Party.id))
        .filter(Party.status == PartyStatus.ACTIVE)
        .scalar()
        or 0
    )
    total_rented = (
        db.query(func.coalesce(func.sum(AvailableStock.RentedOutQty), 0)).scalar() or 0
    )
    total_available = (
        db.query(func.coalesce(func.sum(AvailableStock.availableQty), 0)).scalar() or 0
    )
    total_rentals = db.query(func.count(RentOutTxn.id)).scalar() or 0
    total_returns = db.query(func.count(ReturnTxn.id)).scalar() or 0

    return DashboardStats(
        totalItems=total_items,
        totalParties=total_parties,
        activeParties=active_parties,
        totalRentedOutQty=total_rented,
        totalAvailableQty=total_available,
        totalRentals=total_rentals,
        totalReturns=total_returns,
    )
