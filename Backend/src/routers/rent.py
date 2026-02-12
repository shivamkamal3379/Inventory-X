from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.transactions import RentOutTxnCreate, RentOutTxnOut
from src.services.transactions import rentout_service
# Import stock service to update inventory if needed
# from src.services.inventory import stock_service

router = APIRouter(prefix="/rent", tags=["rent"])


@router.post("/", response_model=RentOutTxnOut)
def create_rent_out(txn: RentOutTxnCreate, db: Session = Depends(get_db)):
    return rentout_service.create(db, obj_in=txn)


@router.get("/", response_model=List[RentOutTxnOut])
def read_rent_outs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return rentout_service.get_multi(db, skip=skip, limit=limit)
