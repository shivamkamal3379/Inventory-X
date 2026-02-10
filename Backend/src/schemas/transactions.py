from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RentOutTxnBase(BaseModel):
    partyId: str
    contractId: Optional[int] = None
    PartyName: Optional[str] = None
    agentId: Optional[int] = None
    AgentName: Optional[str] = None
    Item: Optional[str] = None
    itemQty: int


class RentOutTxnCreate(RentOutTxnBase):
    pass


class RentOutTxnOut(RentOutTxnBase):
    id: int
    TxnDate: datetime

    class Config:
        from_attributes = True


class ReturnTxnBase(BaseModel):
    partyId: str
    contractId: Optional[int] = None
    PartyName: Optional[str] = None
    agentId: Optional[int] = None
    AgentName: Optional[str] = None
    Item: Optional[str] = None
    itemQty: int


class ReturnTxnCreate(ReturnTxnBase):
    pass


class ReturnTxnOut(ReturnTxnBase):
    id: int
    TxnDate: datetime

    class Config:
        from_attributes = True
