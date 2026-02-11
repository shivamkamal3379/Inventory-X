from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.core.database import get_db
from src.schemas.people import AgentCreate, AgentOut, AgentBase, AgentUpdate
from src.services.people import agent_service

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/", response_model=AgentOut)
def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    return agent_service.create(db, obj_in=agent)


@router.get("/", response_model=List[AgentOut])
def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return agent_service.get_multi(db, skip=skip, limit=limit)


@router.get("/{agent_id}", response_model=AgentOut)
def read_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_service.update(db, db_obj=agent, obj_in=agent_in)
    return agent


@router.delete("/{agent_id}", response_model=AgentOut)
def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = agent_service.get(db, id=agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent = agent_service.remove(db, id=agent_id)
    return agent
