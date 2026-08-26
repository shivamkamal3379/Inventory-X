from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.routers.deps import Pagination
from src.schemas.people import AgentCreate, AgentOut, AgentUpdate
from src.services.people import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentOut, status_code=status.HTTP_201_CREATED)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_service.create(db, obj_in=agent)


@router.get("/", response_model=list[AgentOut])
def read_agents(
    page: Pagination = Depends(),
    q: str | None = Query(default=None, description="Search name or mobile"),
    db: Session = Depends(get_db),
):
    return agent_service.search(db, q=q, skip=page.skip, limit=page.limit)


@router.get("/{agent_id}", response_model=AgentOut)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent_service.update(db, db_obj=agent, obj_in=agent_in)


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    agent_service.remove(db, id=agent_id)
