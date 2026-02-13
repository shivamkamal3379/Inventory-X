from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.transactions import ReturnTxnCreate, ReturnTxnOut
from src.services.transactions import return_service

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("/", response_model=ReturnTxnOut)
def create_return(txn: ReturnTxnCreate, db: Session = Depends(get_db)):
    return return_service.create(db, obj_in=txn)


@router.get("/", response_model=List[ReturnTxnOut])
def read_returns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return return_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{txn_id}", response_model=ReturnTxnOut)
def read_return(txn_id: int, db: Session = Depends(get_db)):
    txn = return_service.get(db, id=txn_id)
    if not txn:
        raise HTTPException(status_code=404, detail="Return transaction not found")
    return txn


@router.get("/party/{party_id}", response_model=List[ReturnTxnOut])
def read_returns_by_party(party_id: str, db: Session = Depends(get_db)):
    return return_service.get_by_party(db, party_id=party_id)
