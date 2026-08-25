from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.routers.deps import Pagination
from src.schemas.inventory import (
    ItemCreate,
    ItemOut,
    ItemUpdate,
    ItemWithStockOut,
    StockAdjust,
    StockOut,
)
from src.services.inventory import get_stock, item_service

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    """Create an item, its stock row, and optionally its rental price."""
    return item_service.create(db, obj_in=item)


@router.get("/", response_model=list[ItemWithStockOut])
def read_items(
    page: Pagination = Depends(),
    q: str | None = Query(default=None, description="Search name or description"),
    db: Session = Depends(get_db),
):
    """Items with live stock and price folded in, so the inventory table needs
    exactly one request rather than one per row."""
    return item_service.list_with_stock(db, q=q, skip=page.skip, limit=page.limit)


@router.get("/{item_id}", response_model=ItemOut)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item(item_id: int, item_in: ItemUpdate, db: Session = Depends(get_db)):
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item_service.update(db, db_obj=item, obj_in=item_in)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Deleting an item cascades to its stock and price rows.

    Refused while units are still rented out, and refused by the database if the
    item is referenced by any ledger entry (FK ondelete=RESTRICT) — deleting it
    would silently rewrite rental history.
    """
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    stock = get_stock(db, item_id)
    if stock and stock.RentedOutQty > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete: {stock.RentedOutQty} unit(s) are rented out.",
        )
    item_service.remove(db, id=item_id)


@router.get("/{item_id}/stock", response_model=StockOut)
def read_item_stock(item_id: int, db: Session = Depends(get_db)):
    stock = get_stock(db, item_id)
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock info not found")
    return stock


@router.put("/{item_id}/stock", response_model=StockOut)
def adjust_item_stock(item_id: int, payload: StockAdjust, db: Session = Depends(get_db)):
    """Set a new master quantity (e.g. after buying more units or writing some off)."""
    item = item_service.get(db, id=item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    item_service.update(db, db_obj=item, obj_in={"qty": payload.qty})
    return get_stock(db, item_id)
