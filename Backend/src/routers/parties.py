from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.people import PartyStatus
from src.routers.deps import Pagination
from src.schemas.people import PartyCreate, PartyOut, PartyUpdate
from src.services import transactions as txn_svc
from src.services.people import party_service

router = APIRouter(prefix="/parties", tags=["parties"])


@router.post("/", response_model=PartyOut, status_code=status.HTTP_201_CREATED)
def create_party(party: PartyCreate, db: Session = Depends(get_db)):
    # Checked up front so a duplicate id returns a clear 409 rather than
    # surfacing as a raw IntegrityError.
    if party_service.exists(db, party_id=party.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Party id '{party.id}' already exists.",
        )
    return party_service.create(db, obj_in=party)


@router.get("/", response_model=list[PartyOut])
def read_parties(
    page: Pagination = Depends(),
    q: str | None = Query(default=None, description="Search name, mobile or id"),
    status_filter: PartyStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return party_service.search(
        db,
        q=q,
        status=status_filter.value if status_filter else None,
        skip=page.skip,
        limit=page.limit,
    )


@router.get("/{party_id}", response_model=PartyOut)
def read_party(party_id: str, db: Session = Depends(get_db)):
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")
    return party


@router.put("/{party_id}", response_model=PartyOut)
def update_party(party_id: str, party_in: PartyUpdate, db: Session = Depends(get_db)):
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")
    return party_service.update(db, db_obj=party, obj_in=party_in)


@router.get("/{party_id}/ledger")
def read_party_ledger(
    party_id: str,
    page: Pagination = Depends(),
    db: Session = Depends(get_db),
):
    """Full statement for one party: contracts, returns, payments and balance."""
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")

    contracts = txn_svc.list_contracts(db, party_id=party_id, skip=page.skip, limit=page.limit)
    returns = txn_svc.list_returns(db, party_id=party_id, skip=page.skip, limit=page.limit)
    payments = txn_svc.list_payments(db, party_id=party_id, skip=page.skip, limit=page.limit)

    return {
        "party": PartyOut.model_validate(party),
        "contracts": [txn_svc.contract_summary(c) for c in contracts],
        "returns": returns,
        "payments": payments,
        "totals": {
            "rentCharged": round(sum(r.rentCharged for r in returns), 2),
            "advances": round(sum(c.advancePaid for c in contracts), 2),
            "paid": round(sum(p.amount for p in payments), 2),
            "balance": party.balance,
            "activeItems": party.activeItems,
            "openContracts": sum(1 for c in contracts if c.status.value in ("open", "partial")),
        },
    }


@router.delete("/{party_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_party(party_id: str, db: Session = Depends(get_db)):
    """Refused while the party still holds items or owes money.

    The ledger FKs are ondelete=RESTRICT, so a party with any transaction history
    cannot be deleted at all — that history is the business record.
    """
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Party not found")
    if (party.activeItems or 0) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Party still holds {party.activeItems} item(s).",
        )
    if (party.balance or 0) != 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Party has an outstanding balance of {party.balance}.",
        )
    party_service.remove(db, id=party_id)
