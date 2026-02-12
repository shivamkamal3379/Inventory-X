from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.people import PartyCreate, PartyOut, PartyBase, PartyUpdate
from src.services.people import party_service

router = APIRouter(prefix="/parties", tags=["parties"])


@router.post("/", response_model=PartyOut)
def create_party(party: PartyCreate, db: Session = Depends(get_db)):
    # Check if existing party logic?
    # For now simple create
    return party_service.create(db, obj_in=party)


@router.get("/", response_model=List[PartyOut])
def read_parties(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return party_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{party_id}", response_model=PartyOut)
def read_party(party_id: str, db: Session = Depends(get_db)):
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party


@router.put("/{party_id}", response_model=PartyOut)
def update_party(party_id: str, party_in: PartyUpdate, db: Session = Depends(get_db)):
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    party = party_service.update(db, db_obj=party, obj_in=party_in)
    return party


@router.delete("/{party_id}", response_model=PartyOut)
def delete_party(party_id: str, db: Session = Depends(get_db)):
    party = party_service.get(db, id=party_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    party = party_service.remove(db, id=party_id)
    return party
