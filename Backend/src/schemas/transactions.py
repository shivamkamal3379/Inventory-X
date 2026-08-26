from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models.transactions import ContractStatus, RentFrequency


class ContractLineIn(BaseModel):
    """One item on a new rental.

    `ratePerUnit` is not accepted from the client — it is read from RentalPrice
    server-side so the ledger cannot be manipulated by a crafted request.
    """

    itemId: int
    qty: int = Field(gt=0, le=1_000_000)
    rentFrequency: RentFrequency | None = None


class ContractCreate(BaseModel):
    partyId: str = Field(min_length=1, max_length=50)
    items: list[ContractLineIn] = Field(min_length=1, max_length=100)
    agentId: int | None = None
    startDate: datetime | None = None
    expectedReturnDate: datetime | None = None
    advancePaid: float = Field(default=0.0, ge=0)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("items")
    @classmethod
    def _no_duplicate_items(cls, v: list[ContractLineIn]) -> list[ContractLineIn]:
        ids = [line.itemId for line in v]
        if len(ids) != len(set(ids)):
            raise ValueError("The same item appears more than once; combine it into a single line.")
        return v


class ContractLineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    itemId: int
    Item: str | None = None
    qty: int
    returnedQty: int
    outstandingQty: int
    ratePerUnit: float
    rentFrequency: str
    accruedRent: float


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    contractId: int
    contractNo: str
    partyId: str
    PartyName: str | None = None
    agentId: int | None = None
    AgentName: str | None = None
    status: ContractStatus
    startDate: datetime
    expectedReturnDate: datetime | None = None
    closedAt: datetime | None = None
    advancePaid: float
    accruedRent: float
    totalPaid: float
    balanceDue: float
    notes: str | None = None
    createdAt: datetime
    lines: list[ContractLineOut] = []


class ContractSummaryOut(BaseModel):
    """List-view projection — omits line items so the contracts table is one query."""

    model_config = ConfigDict(from_attributes=True)

    contractId: int
    contractNo: str
    partyId: str
    PartyName: str | None = None
    AgentName: str | None = None
    status: ContractStatus
    startDate: datetime
    expectedReturnDate: datetime | None = None
    advancePaid: float
    accruedRent: float
    totalPaid: float
    balanceDue: float
    itemCount: int = 0
    outstandingQty: int = 0


class ReturnLineIn(BaseModel):
    lineId: int
    qty: int = Field(gt=0, le=1_000_000)


class ReturnCreate(BaseModel):
    items: list[ReturnLineIn] = Field(min_length=1, max_length=100)
    returnDate: datetime | None = None
    amountPaid: float = Field(default=0.0, ge=0)
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("items")
    @classmethod
    def _no_duplicate_lines(cls, v: list[ReturnLineIn]) -> list[ReturnLineIn]:
        ids = [line.lineId for line in v]
        if len(ids) != len(set(ids)):
            raise ValueError("The same contract line appears more than once.")
        return v


class ReturnTxnOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contractId: int
    lineId: int | None = None
    partyId: str
    PartyName: str | None = None
    itemId: int
    Item: str | None = None
    qty: int
    returnDate: datetime
    daysHeld: int
    periodsCharged: int
    ratePerUnit: float
    rentCharged: float
    amountPaid: float


class ReturnResultOut(BaseModel):
    """What a return produced: the receipts, plus the contract's new state."""

    returns: list[ReturnTxnOut]
    totalCharged: float
    totalPaid: float
    contract: ContractOut


class PaymentCreate(BaseModel):
    amount: float = Field(gt=0)
    method: str | None = Field(default=None, max_length=30)
    notes: str | None = Field(default=None, max_length=2000)


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contractId: int | None = None
    partyId: str
    amount: float
    method: str | None = None
    notes: str | None = None
    paidAt: datetime


class QuoteLine(BaseModel):
    lineId: int
    itemId: int
    Item: str | None = None
    qty: int
    ratePerUnit: float
    rentFrequency: str
    daysHeld: int
    periodsCharged: int
    rentCharged: float


class ReturnQuote(BaseModel):
    """A dry-run of a return, so the UI can show the bill before committing."""

    contractId: int
    contractNo: str
    asOf: datetime
    lines: list[QuoteLine]
    subtotal: float
    advanceApplied: float
    alreadyPaid: float
    netDue: float


class ActivityOut(BaseModel):
    id: int
    type: str  # "RENTAL" | "RETURN" | "PAYMENT"
    contractId: int | None = None
    contractNo: str | None = None
    partyId: str
    PartyName: str | None = None
    Item: str | None = None
    itemQty: int = 0
    amount: float = 0.0
    TxnDate: datetime
