from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from src.models.people import Agent, Party
from src.schemas.people import AgentCreate, AgentUpdate, PartyCreate, PartyUpdate
from src.services.base import CRUDBase


class CRUDAgent(CRUDBase[Agent, AgentCreate, AgentUpdate]):
    def search(self, db: Session, *, q: str | None, skip: int = 0, limit: int = 100) -> list[Agent]:
        stmt = select(Agent)
        if q:
            term = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Agent.AgentName).like(term),
                    func.lower(Agent.mobile).like(term),
                )
            )
        stmt = stmt.order_by(Agent.agentId.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())


class CRUDParty(CRUDBase[Party, PartyCreate, PartyUpdate]):
    def search(
        self,
        db: Session,
        *,
        q: str | None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Party]:
        stmt = select(Party)
        if q:
            term = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Party.name).like(term),
                    func.lower(Party.mobile).like(term),
                    func.lower(Party.id).like(term),
                )
            )
        if status:
            stmt = stmt.where(Party.status == status)
        stmt = stmt.order_by(Party.dateCreated.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def exists(self, db: Session, *, party_id: str) -> bool:
        return db.get(Party, party_id) is not None


agent_service = CRUDAgent(Agent)
party_service = CRUDParty(Party)
