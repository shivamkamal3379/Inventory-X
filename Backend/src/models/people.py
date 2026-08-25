import enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from src.core.database import Base


class Agent(Base):
    __tablename__ = "t_Agents"

    agentId: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    AgentName: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    mobile: Mapped[str] = mapped_column(String(20), nullable=False)
    aadhar: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    parties: Mapped[list["Party"]] = relationship(back_populates="agent")


class PartyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAYMENT_DUE = "payment_due"
    DEFAULT = "default"
    CLOSED = "closed"


# Persist the lowercase *values* ("active"), not the member names ("ACTIVE"),
# so what the database holds matches what the API returns.
party_status_enum = SAEnum(
    PartyStatus,
    name="party_status",
    values_callable=lambda enum_cls: [member.value for member in enum_cls],
)


class Party(Base):
    __tablename__ = "t_party"
    __table_args__ = (
        CheckConstraint('"activeItems" >= 0', name="ck_party_active_items_non_negative"),
    )

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    mobile: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    aadhaar: Mapped[str | None] = mapped_column(String(20))
    secondaryMobile: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(String(255))
    agentId: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("t_Agents.agentId", ondelete="SET NULL"), index=True
    )
    agentName: Mapped[str | None] = mapped_column(String(100))
    siteAddress: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[PartyStatus] = mapped_column(
        party_status_enum, default=PartyStatus.ACTIVE, nullable=False, index=True
    )
    balance: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    activeItems: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    dateCreated: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[object | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    agent: Mapped["Agent | None"] = relationship(back_populates="parties")
