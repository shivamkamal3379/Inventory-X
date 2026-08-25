"""Read-only payment history. Payments are created via POST /contracts/{id}/payment."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.routers.deps import Pagination
from src.schemas.transactions import PaymentOut
from src.services import transactions as svc

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=list[PaymentOut])
def list_payments(
    page: Pagination = Depends(),
    party_id: str | None = Query(default=None, alias="partyId"),
    db: Session = Depends(get_db),
):
    return svc.list_payments(db, party_id=party_id, skip=page.skip, limit=page.limit)
