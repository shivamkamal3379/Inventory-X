from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.transactions import ReturnTxnCreate, ReturnTxnOut
from src.services.transactions import return_service
# Import stock service to update inventory if needed

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("/", response_model=ReturnTxnOut)
def create_return(txn: ReturnTxnCreate, db: Session = Depends(get_db)):
    return return_service.create(db, obj_in=txn)


@router.get("/", response_model=List[ReturnTxnOut])
def read_returns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return return_service.get_multi(db, skip=skip, limit=limit)
