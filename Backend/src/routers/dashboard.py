from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.inventory import AvailableStock, Item
from src.models.people import Party, PartyStatus
from src.models.transactions import (
    ContractLine,
    ContractStatus,
    Payment,
    RentalContract,
    ReturnTxn,
)
from src.schemas.transactions import ActivityOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class DashboardStats(BaseModel):
    totalItems: int = 0
    totalParties: int = 0
    activeParties: int = 0
    partiesWithDues: int = 0
    totalRentedOutQty: int = 0
    totalAvailableQty: int = 0
    openContracts: int = 0
    overdueContracts: int = 0
    totalContracts: int = 0
    totalReturns: int = 0
    outstandingBalance: float = 0.0
    revenueThisMonth: float = 0.0
    utilisationPct: float = 0.0


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    def scalar(stmt):
        return db.execute(stmt).scalar() or 0

    now = datetime.now(UTC)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    rented = scalar(select(func.coalesce(func.sum(AvailableStock.RentedOutQty), 0)))
    available = scalar(select(func.coalesce(func.sum(AvailableStock.availableQty), 0)))
    total_units = rented + available

    return DashboardStats(
        totalItems=scalar(select(func.count(Item.itemId))),
        totalParties=scalar(select(func.count(Party.id))),
        activeParties=scalar(
            select(func.count(Party.id)).where(Party.status == PartyStatus.ACTIVE)
        ),
        partiesWithDues=scalar(
            select(func.count(Party.id)).where(Party.status == PartyStatus.PAYMENT_DUE)
        ),
        totalRentedOutQty=rented,
        totalAvailableQty=available,
        openContracts=scalar(
            select(func.count(RentalContract.contractId)).where(
                RentalContract.status.in_([ContractStatus.OPEN, ContractStatus.PARTIAL])
            )
        ),
        overdueContracts=scalar(
            select(func.count(RentalContract.contractId)).where(
                RentalContract.status.in_([ContractStatus.OPEN, ContractStatus.PARTIAL]),
                RentalContract.expectedReturnDate.is_not(None),
                RentalContract.expectedReturnDate < now,
            )
        ),
        totalContracts=scalar(select(func.count(RentalContract.contractId))),
        totalReturns=scalar(select(func.count(ReturnTxn.id))),
        outstandingBalance=round(
            float(scalar(select(func.coalesce(func.sum(Party.balance), 0.0)))), 2
        ),
        revenueThisMonth=round(
            float(
                scalar(
                    select(func.coalesce(func.sum(ReturnTxn.rentCharged), 0.0)).where(
                        ReturnTxn.returnDate >= month_start
                    )
                )
            ),
            2,
        ),
        utilisationPct=round(100.0 * rented / total_units, 1) if total_units else 0.0,
    )


@router.get("/activity", response_model=list[ActivityOut])
def get_recent_activity(
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Merged rentals / returns / payments feed, newest first.

    The frontend dashboard has always called this endpoint; it did not exist
    before, so 'Recent Activity' silently rendered empty.
    """
    contracts = (
        db.execute(
            select(RentalContract)
            .order_by(RentalContract.startDate.desc(), RentalContract.contractId.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    returns = (
        db.execute(
            select(ReturnTxn)
            .order_by(ReturnTxn.returnDate.desc(), ReturnTxn.id.desc())
            .limit(limit)
        )
        .scalars()
        .all()
    )
    payments = (
        db.execute(select(Payment).order_by(Payment.paidAt.desc(), Payment.id.desc()).limit(limit))
        .scalars()
        .all()
    )

    unit_counts = dict(
        db.execute(
            select(ContractLine.contractId, func.coalesce(func.sum(ContractLine.qty), 0))
            .where(ContractLine.contractId.in_([c.contractId for c in contracts] or [-1]))
            .group_by(ContractLine.contractId)
        ).all()
    )

    feed: list[ActivityOut] = []
    feed += [
        ActivityOut(
            id=c.contractId,
            type="RENTAL",
            contractId=c.contractId,
            contractNo=c.contractNo,
            partyId=c.partyId,
            PartyName=c.PartyName,
            Item=f"{len(c.lines)} item(s)" if c.lines else None,
            itemQty=int(unit_counts.get(c.contractId, 0)),
            amount=c.advancePaid,
            TxnDate=c.startDate,
        )
        for c in contracts
    ]
    feed += [
        ActivityOut(
            id=r.id,
            type="RETURN",
            contractId=r.contractId,
            partyId=r.partyId,
            PartyName=r.PartyName,
            Item=r.Item,
            itemQty=r.qty,
            amount=r.rentCharged,
            TxnDate=r.returnDate,
        )
        for r in returns
    ]
    feed += [
        ActivityOut(
            id=p.id,
            type="PAYMENT",
            contractId=p.contractId,
            partyId=p.partyId,
            Item=None,
            itemQty=0,
            amount=p.amount,
            TxnDate=p.paidAt,
        )
        for p in payments
    ]

    feed.sort(key=lambda a: a.TxnDate, reverse=True)
    return feed[:limit]


class TrendPoint(BaseModel):
    date: str
    revenue: float = 0.0
    rentals: int = 0


@router.get("/trend", response_model=list[TrendPoint])
def get_revenue_trend(
    days: int = Query(default=30, ge=7, le=180),
    db: Session = Depends(get_db),
):
    """Daily revenue and rental counts, zero-filled so charts have no gaps."""
    now = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    start = now - timedelta(days=days - 1)

    revenue_rows = db.execute(
        select(
            func.date(ReturnTxn.returnDate).label("d"),
            func.coalesce(func.sum(ReturnTxn.rentCharged), 0.0),
        )
        .where(ReturnTxn.returnDate >= start)
        .group_by(func.date(ReturnTxn.returnDate))
    ).all()
    rental_rows = db.execute(
        select(
            func.date(RentalContract.startDate).label("d"),
            func.count(RentalContract.contractId),
        )
        .where(RentalContract.startDate >= start)
        .group_by(func.date(RentalContract.startDate))
    ).all()

    revenue = {str(d): float(v or 0) for d, v in revenue_rows}
    rentals = {str(d): int(v or 0) for d, v in rental_rows}

    return [
        TrendPoint(
            date=(key := (start + timedelta(days=i)).strftime("%Y-%m-%d")),
            revenue=round(revenue.get(key, 0.0), 2),
            rentals=rentals.get(key, 0),
        )
        for i in range(days)
    ]


class TopItem(BaseModel):
    itemId: int
    name: str
    timesRented: int
    unitsRented: int
    revenue: float = 0.0


@router.get("/top-items", response_model=list[TopItem])
def get_top_items(
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(
            Item.itemId,
            Item.name,
            func.count(ContractLine.id),
            func.coalesce(func.sum(ContractLine.qty), 0),
            func.coalesce(func.sum(ContractLine.accruedRent), 0.0),
        )
        .join(ContractLine, ContractLine.itemId == Item.itemId)
        .group_by(Item.itemId, Item.name)
        .order_by(func.coalesce(func.sum(ContractLine.qty), 0).desc())
        .limit(limit)
    ).all()

    return [
        TopItem(
            itemId=r[0],
            name=r[1],
            timesRented=int(r[2]),
            unitsRented=int(r[3]),
            revenue=round(float(r[4]), 2),
        )
        for r in rows
    ]
