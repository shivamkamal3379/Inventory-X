from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RentOutTxnBase(BaseModel):
    partyId: str
    itemId: int
    contractId: Optional[int] = None
    PartyName: Optional[str] = None
    agentId: Optional[int] = None
    AgentName: Optional[str] = None
    Item: Optional[str] = None
    itemQty: int
    rentAmount: Optional[float] = None
    paidAmount: Optional[float] = 0.0


class RentOutTxnCreate(RentOutTxnBase):
    pass


class RentOutTxnOut(RentOutTxnBase):
    id: int
    TxnDate: datetime

    class Config:
        from_attributes = True


class ReturnTxnBase(BaseModel):
    partyId: str
    itemId: int
    contractId: Optional[int] = None
    PartyName: Optional[str] = None
    agentId: Optional[int] = None
    AgentName: Optional[str] = None
    Item: Optional[str] = None
    itemQty: int
    refundAmount: Optional[float] = 0.0


class ReturnTxnCreate(ReturnTxnBase):
    pass


class ReturnTxnOut(ReturnTxnBase):
    id: int
    TxnDate: datetime

    class Config:
        from_attributes = True
