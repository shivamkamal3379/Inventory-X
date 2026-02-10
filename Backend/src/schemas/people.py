from pydantic import BaseModel
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


class PartyCreate(PartyBase):
    id: str
    pass


class PartyOut(PartyBase):
    id: str
    dateCreated: datetime

    class Config:
        from_attributes = True
