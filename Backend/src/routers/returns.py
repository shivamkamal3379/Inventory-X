"""Read-only return history. Returns are created via POST /contracts/{id}/return."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.routers.deps import Pagination
from src.schemas.transactions import ReturnTxnOut
from src.services import transactions as svc

router = APIRouter(prefix="/returns", tags=["returns"])


@router.get("/", response_model=list[ReturnTxnOut])
def list_returns(
    page: Pagination = Depends(),
    party_id: str | None = Query(default=None, alias="partyId"),
    db: Session = Depends(get_db),
):
    return svc.list_returns(db, party_id=party_id, skip=page.skip, limit=page.limit)
