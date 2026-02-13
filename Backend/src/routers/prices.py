from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.inventory import RentalPriceCreate, RentalPriceOut
from src.services.inventory import price_service

router = APIRouter(prefix="/prices", tags=["prices"])


@router.post("/", response_model=RentalPriceOut)
def create_rental_price(price: RentalPriceCreate, db: Session = Depends(get_db)):
    # Check if price already exists for this item
    existing = price_service.get(db, id=price.itemId)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Rental price already exists for this item. Use PUT to update.",
        )
    return price_service.create(db, obj_in=price)


@router.get("/", response_model=List[RentalPriceOut])
def read_rental_prices(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return price_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=RentalPriceOut)
def read_rental_price(item_id: int, db: Session = Depends(get_db)):
    price = price_service.get(db, id=item_id)
    if not price:
        raise HTTPException(
            status_code=404, detail="Rental price not found for this item"
        )
    return price
