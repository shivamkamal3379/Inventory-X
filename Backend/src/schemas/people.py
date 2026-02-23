from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from src.models.people import PartyStatus


class AgentBase(BaseModel):
    AgentName: str
    mobile: str
    aadhar: Optional[str] = None
    email: Optional[str] = None


class AgentCreate(AgentBase):
    pass


class AgentUpdate(AgentBase):
    AgentName: Optional[str] = None
    mobile: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    pass


class AgentOut(AgentBase):
    agentId: int

    class Config:
        from_attributes = True


class PartyBase(BaseModel):
    name: str
    mobile: str
    aadhaar: Optional[str] = None
    secondaryMobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    agentId: Optional[int] = None
    agentName: Optional[str] = None
    siteAddress: Optional[str] = None
    status: PartyStatus = PartyStatus.ACTIVE
    balance: Optional[float] = 0.0
    activeItems: Optional[int] = 0


class PartyCreate(PartyBase):
    id: str
    pass


class PartyUpdate(PartyBase):
    name: Optional[str] = None
    mobile: Optional[str] = None
    id: Optional[str] = None
    pass


class PartyOut(PartyBase):
    id: str
    dateCreated: datetime

    class Config:
        from_attributes = True
