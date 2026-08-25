"""Rental contracts: the invoice-level API.

Replaces the old per-item POST /rent/ + POST /returns/ pair. A rental is now one
call carrying every item, which is what makes a printable bill, a single return,
and duration-based billing possible at all.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.transactions import ContractStatus
from src.routers.deps import Pagination
from src.schemas.transactions import (
    ContractCreate,
    ContractOut,
    ContractSummaryOut,
    PaymentCreate,
    PaymentOut,
    ReturnCreate,
    ReturnQuote,
    ReturnResultOut,
)
from src.services import transactions as svc

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.post("/", response_model=ContractOut, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    """Rent items out under a single contract.

    Reserves stock for every line, records the rate in force at pickup, and takes
    any advance as a credit against the party. No rent is charged yet — it accrues
    when the goods come back and the duration is known.
    """
    return svc.create_contract(db, obj_in=payload)


@router.get("/", response_model=list[ContractSummaryOut])
def list_contracts(
    page: Pagination = Depends(),
    party_id: str | None = Query(default=None, alias="partyId"),
    contract_status: ContractStatus | None = Query(default=None, alias="status"),
    q: str | None = Query(default=None, description="Search contract no or party name"),
    db: Session = Depends(get_db),
):
    contracts = svc.list_contracts(
        db,
        party_id=party_id,
        contract_status=contract_status.value if contract_status else None,
        q=q,
        skip=page.skip,
        limit=page.limit,
    )
    return [svc.contract_summary(c) for c in contracts]


@router.get("/{contract_id}", response_model=ContractOut)
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    return svc.get_contract(db, contract_id)


@router.get("/{contract_id}/quote", response_model=ReturnQuote)
def quote_contract_return(
    contract_id: int,
    as_of: datetime | None = Query(default=None, alias="asOf"),
    db: Session = Depends(get_db),
):
    """Dry-run the bill for returning everything still out.

    Changes nothing — it exists so the counter can show the customer the amount
    before committing the return.
    """
    return svc.quote_return(db, contract_id=contract_id, as_of=as_of)


@router.post(
    "/{contract_id}/return", response_model=ReturnResultOut, status_code=status.HTTP_201_CREATED
)
def return_items(contract_id: int, payload: ReturnCreate, db: Session = Depends(get_db)):
    """Take some or all items back, charging rent for the period held."""
    return svc.process_return(db, contract_id=contract_id, obj_in=payload)


@router.post(
    "/{contract_id}/payment", response_model=PaymentOut, status_code=status.HTTP_201_CREATED
)
def add_payment(contract_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    """Record a payment against the contract, reducing the party's balance."""
    return svc.record_payment(db, contract_id=contract_id, obj_in=payload)
