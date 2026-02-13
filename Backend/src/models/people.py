from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base
import enum


class Agent(Base):
    __tablename__ = "t_Agents"

    agentId = Column(Integer, primary_key=True, autoincrement=True)
    AgentName = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)  # Changed to String for phone numbers
    aadhar = Column(String(20))  # Changed to String
    email = Column(String(100))

    parties = relationship("Party", back_populates="agent")


class PartyStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAYMENT_DUE = "payment_due"
    DEFAULT = "default"
    CLOSED = "closed"


class Party(Base):
    __tablename__ = "t_party"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    mobile = Column(String(20), nullable=False)
    aadhaar = Column(String(20))
    secondaryMobile = Column(String(20))
    email = Column(String(100))
    address = Column(String(255))
    agentId = Column(Integer, ForeignKey("t_Agents.agentId"))
    agentName = Column(String(100))  # Denormalized or just a field? Keeping as per ERD
    siteAddress = Column(String(255))
    status = Column(Enum(PartyStatus), default=PartyStatus.ACTIVE)
    balance = Column(Float, default=0.0)
    activeItems = Column(Integer, default=0)
    dateCreated = Column(DateTime, default=func.now())

    agent = relationship("Agent", back_populates="parties")
