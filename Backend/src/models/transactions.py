from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class RentOutTxn(Base):
    __tablename__ = "rentoutTxn"

    # ERD says partyId PK, but partyId is FK to Party.
    # Likely this is a transaction definition where (partyId, contractId) or just contractId is PK.
    # ERD: partyId string pk. This implies one txn per party? Unlikely.
    # Usually transaction table has its own ID.
    # Or maybe it's a composite PK? content: `partyId string pk`, `contractId number`.
    # I will assume contractId + partyId or just a surrogate key.
    # Given the structure, I'll make a composite PK or auto ID.
    # ERD shows `partyId string pk`. This might be a mistake in ERD or strictly one active rental per party?
    # Reading closely: `multiple rows to be entered in DB`. So likely not PK on partyId alone.
    # I will add an auto-increment ID or use contractId if unique.
    # I will add `id` as primary key to be safe and standard.

    id = Column(Integer, primary_key=True, autoincrement=True)
    partyId = Column(String(50), ForeignKey("t_party.id"))
    contractId = Column(Integer)  # Maybe grouped by contract
    PartyName = Column(String(100))
    agentId = Column(Integer, ForeignKey("t_Agents.agentId"))
    AgentName = Column(String(100))
    Item = Column(String(100))  # Item Name? Or FK? ERD says string.
    itemQty = Column(Integer)
    TxnDate = Column(DateTime, default=func.now())

    party = relationship(
        "src.models.people.Party"
    )  # String reference to avoid circular import if needed
    agent = relationship("src.models.people.Agent")


class ReturnTxn(Base):
    __tablename__ = "returnTxn"

    id = Column(Integer, primary_key=True, autoincrement=True)
    partyId = Column(String(50), ForeignKey("t_party.id"))
    contractId = Column(Integer)
    PartyName = Column(String(100))
    agentId = Column(Integer, ForeignKey("t_Agents.agentId"))
    AgentName = Column(String(100))
    Item = Column(String(100))
    itemQty = Column(Integer)
    TxnDate = Column(DateTime, default=func.now())

    party = relationship("src.models.people.Party")
    agent = relationship("src.models.people.Agent")
