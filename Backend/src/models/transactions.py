"""Rental contracts, their line items, and returns.

Model rationale
---------------
A rental is an *invoice*: one party, one date, many items. The previous design
had a flat `rentoutTxn` row per item with no shared identifier, so a three-item
rental became three unrelated ledger entries that could never be printed as one
bill or returned together.

Rent is *accrued on return*, not charged up front, because the amount depends on
how long the goods were actually held — which is unknown at rent-out time. A
contract therefore carries an optional advance, and each return computes
`rate x qty x periods_held` and posts it to the party's balance.
"""

import enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class ContractStatus(str, enum.Enum):
    OPEN = "open"  # nothing returned yet
    PARTIAL = "partial"  # some items back, some still out
    CLOSED = "closed"  # everything returned
    CANCELLED = "cancelled"


class RentFrequency(str, enum.Enum):
    """How often the rate accrues. Values are the billing period in days."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


PERIOD_DAYS: dict[str, int] = {
    RentFrequency.DAILY.value: 1,
    RentFrequency.WEEKLY.value: 7,
    RentFrequency.MONTHLY.value: 30,
}

contract_status_enum = SAEnum(
    ContractStatus,
    name="contract_status",
    values_callable=lambda e: [m.value for m in e],
)


class RentalContract(Base):
    """One rent-out event: the invoice header."""

    __tablename__ = "rentalContract"
    __table_args__ = (
        CheckConstraint('"advancePaid" >= 0', name="ck_contract_advance_non_negative"),
        CheckConstraint('"accruedRent" >= 0', name="ck_contract_accrued_non_negative"),
        CheckConstraint('"totalPaid" >= 0', name="ck_contract_paid_non_negative"),
        Index("ix_contract_party_date", "partyId", "startDate"),
    )

    contractId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # Human-facing invoice number, e.g. INV-000042.
    contractNo: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)

    partyId: Mapped[str] = mapped_column(
        String(50), ForeignKey("t_party.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    PartyName: Mapped[str | None] = mapped_column(String(100))
    agentId: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("t_Agents.agentId", ondelete="SET NULL")
    )
    AgentName: Mapped[str | None] = mapped_column(String(100))

    status: Mapped[ContractStatus] = mapped_column(
        contract_status_enum, default=ContractStatus.OPEN, nullable=False, index=True
    )

    startDate: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    expectedReturnDate: Mapped[object | None] = mapped_column(DateTime(timezone=True))
    closedAt: Mapped[object | None] = mapped_column(DateTime(timezone=True))

    # Money taken before any rent has accrued; sits as a credit on the party.
    advancePaid: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    # Rent actually charged so far, accumulated as items come back.
    accruedRent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    totalPaid: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    notes: Mapped[str | None] = mapped_column(Text)
    createdAt: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lines: Mapped[list["ContractLine"]] = relationship(
        back_populates="contract", cascade="all, delete-orphan", passive_deletes=True
    )
    returns: Mapped[list["ReturnTxn"]] = relationship(
        back_populates="contract", cascade="all, delete-orphan", passive_deletes=True
    )
    party: Mapped["Party"] = relationship("src.models.people.Party")  # noqa: F821
    agent: Mapped["Agent | None"] = relationship("src.models.people.Agent")  # noqa: F821

    @property
    def balanceDue(self) -> float:
        return round(self.accruedRent - self.totalPaid - self.advancePaid, 2)


class ContractLine(Base):
    """One item on a contract. `ratePerUnit` is copied at rent-out time so a later
    price change never rewrites the amount a customer was quoted."""

    __tablename__ = "contractLine"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_line_qty_positive"),
        CheckConstraint('"returnedQty" >= 0', name="ck_line_returned_non_negative"),
        CheckConstraint('"returnedQty" <= qty', name="ck_line_returned_not_over_qty"),
        CheckConstraint('"ratePerUnit" >= 0', name="ck_line_rate_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contractId: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rentalContract.contractId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    itemId: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_Item.itemId", ondelete="RESTRICT"), nullable=False, index=True
    )
    Item: Mapped[str | None] = mapped_column(String(100))
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    returnedQty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ratePerUnit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rentFrequency: Mapped[str] = mapped_column(
        String(20), default=RentFrequency.DAILY.value, nullable=False
    )
    accruedRent: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    contract: Mapped["RentalContract"] = relationship(back_populates="lines")

    @property
    def outstandingQty(self) -> int:
        return self.qty - self.returnedQty


class ReturnTxn(Base):
    """A return event, carrying the duration maths that produced the charge."""

    __tablename__ = "returnTxn"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_return_qty_positive"),
        CheckConstraint('"daysHeld" >= 0', name="ck_return_days_non_negative"),
        CheckConstraint('"rentCharged" >= 0', name="ck_return_charge_non_negative"),
        Index("ix_return_contract_date", "contractId", "returnDate"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contractId: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("rentalContract.contractId", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lineId: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("contractLine.id", ondelete="SET NULL")
    )
    partyId: Mapped[str] = mapped_column(
        String(50), ForeignKey("t_party.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    PartyName: Mapped[str | None] = mapped_column(String(100))
    itemId: Mapped[int] = mapped_column(
        Integer, ForeignKey("t_Item.itemId", ondelete="RESTRICT"), nullable=False, index=True
    )
    Item: Mapped[str | None] = mapped_column(String(100))

    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    returnDate: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    # The billing trail: how long, at what rate, over how many periods.
    daysHeld: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    periodsCharged: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    ratePerUnit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    rentCharged: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    amountPaid: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    contract: Mapped["RentalContract"] = relationship(back_populates="returns")


class Payment(Base):
    """A payment recorded against a contract outside of rent-out or return."""

    __tablename__ = "payment"
    __table_args__ = (CheckConstraint("amount > 0", name="ck_payment_amount_positive"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    contractId: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("rentalContract.contractId", ondelete="SET NULL"), index=True
    )
    partyId: Mapped[str] = mapped_column(
        String(50), ForeignKey("t_party.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[str | None] = mapped_column(String(30))
    notes: Mapped[str | None] = mapped_column(Text)
    paidAt: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
