from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.routers.deps import Pagination
from src.schemas.inventory import RentalPriceCreate, RentalPriceOut, RentalPriceUpdate
from src.services.inventory import price_service

router = APIRouter(prefix="/prices", tags=["prices"])


@router.post("/", response_model=RentalPriceOut, status_code=status.HTTP_201_CREATED)
def create_rental_price(price: RentalPriceCreate, db: Session = Depends(get_db)):
    if price_service.get(db, id=price.itemId):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Rental price already exists for this item. Use PUT to update.",
        )
    return price_service.create(db, obj_in=price)


@router.get("/", response_model=list[RentalPriceOut])
def read_rental_prices(page: Pagination = Depends(), db: Session = Depends(get_db)):
    return price_service.get_multi(db, skip=page.skip, limit=page.limit)


@router.get("/{item_id}", response_model=RentalPriceOut)
def read_rental_price(item_id: int, db: Session = Depends(get_db)):
    price = price_service.get(db, id=item_id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental price not found for this item",
        )
    return price


@router.put("/{item_id}", response_model=RentalPriceOut)
def update_rental_price(item_id: int, price_in: RentalPriceUpdate, db: Session = Depends(get_db)):
    """Only affects rentals created after this point — historical rentAmounts are
    stored on the ledger row and stay at the price that was actually charged."""
    price = price_service.get(db, id=item_id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental price not found for this item",
        )
    return price_service.update(db, db_obj=price, obj_in=price_in)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rental_price(item_id: int, db: Session = Depends(get_db)):
    price = price_service.get(db, id=item_id)
    if not price:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rental price not found for this item",
        )
    price_service.remove(db, id=item_id)
