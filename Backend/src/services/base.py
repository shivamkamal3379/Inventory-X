"""Generic CRUD helper.

Methods take a `commit` flag so a caller composing several writes (rent-out
touches stock, party and the ledger) can run them in one transaction and commit
once, instead of committing partway and leaving the database half-updated if a
later step fails.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType | None:
        return db.get(self.model, id)

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count(self, db: Session) -> int:
        return db.execute(select(func.count()).select_from(self.model)).scalar_one()

    def create(self, db: Session, *, obj_in: CreateSchemaType, commit: bool = True) -> ModelType:
        db_obj = self.model(**obj_in.model_dump(exclude_unset=False))
        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        else:
            db.flush()
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict,
        commit: bool = True,
    ) -> ModelType:
        # exclude_unset keeps a PATCH-like PUT from nulling every field the
        # client did not mention.
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        if commit:
            db.commit()
            db.refresh(db_obj)
        else:
            db.flush()
        return db_obj

    def remove(self, db: Session, *, id: Any, commit: bool = True) -> ModelType | None:
        obj = db.get(self.model, id)
        if obj is None:
            return None
        db.delete(obj)
        if commit:
            db.commit()
        else:
            db.flush()
        return obj
