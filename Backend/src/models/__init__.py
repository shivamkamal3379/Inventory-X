"""Importing this package registers every model on Base.metadata.

Alembic autogenerate and `Base.metadata.create_all` both rely on that, so the
imports below are load-bearing despite looking unused.
"""

from src.models.auth import User
from src.models.inventory import AvailableStock, Item, RentalPrice
from src.models.people import Agent, Party, PartyStatus
from src.models.transactions import (
    PERIOD_DAYS,
    ContractLine,
    ContractStatus,
    Payment,
    RentalContract,
    RentFrequency,
    ReturnTxn,
)

__all__ = [
    "PERIOD_DAYS",
    "Agent",
    "AvailableStock",
    "ContractLine",
    "ContractStatus",
    "Item",
    "Party",
    "PartyStatus",
    "Payment",
    "RentFrequency",
    "RentalContract",
    "RentalPrice",
    "ReturnTxn",
    "User",
]
