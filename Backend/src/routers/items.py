from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.inventory import (
    ItemCreate,
    ItemOut,
    AvailableStockOut,
    RentalPriceOut,
    ItemUpdate,
)
from src.services.inventory import item_service, stock_service, price_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemOut)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    return item_service.create(db, obj_in=item)


@router.get("/", response_model=List[ItemOut])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return item_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = item_service.update(db, db_obj=item, obj_in=item_in)
    return item


@router.delete("/{item_id}", response_model=ItemOut)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = item_service.remove(db, id=item_id)
    return item


@router.get("/{item_id}/stock", response_model=AvailableStockOut)
def read_item_stock(item_id: int, db: Session = Depends(get_db)):
    stock = stock_service.get(db, id=item_id)
    if not stock:  # Should probably auto-create stock 0 if not exists
        raise HTTPException(status_code=404, detail="Stock info not found")
    return stock
