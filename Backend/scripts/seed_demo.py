#!/usr/bin/env python
"""Populate a database with realistic demo data.

    python scripts/seed_demo.py            # add demo data
    python scripts/seed_demo.py --reset    # wipe business tables first

Refuses to run against ENVIRONMENT=production unless --force is passed, because
--reset deletes every contract, party and item in the target database.

It goes through the service layer rather than raw INSERTs, so the seeded data
obeys the same stock and ledger rules as anything created through the API — the
old DummyData.sql wrote rows directly and never created the AvailableStock rows
the rental flow depends on.
"""

import argparse
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.core.config import settings  # noqa: E402
from src.core.database import Base, SessionLocal, engine  # noqa: E402
from src.core.security import hash_password  # noqa: E402
from src.models.auth import User  # noqa: E402
from src.models.inventory import AvailableStock, Item, RentalPrice  # noqa: E402
from src.models.people import Agent, Party  # noqa: E402
from src.models.transactions import (  # noqa: E402
    ContractLine,
    Payment,
    RentalContract,
    ReturnTxn,
)
from src.schemas.inventory import ItemCreate  # noqa: E402
from src.schemas.people import AgentCreate, PartyCreate  # noqa: E402
from src.schemas.transactions import ContractCreate, ContractLineIn, ReturnCreate  # noqa: E402
from src.services import transactions as txn_svc  # noqa: E402
from src.services.inventory import item_service  # noqa: E402
from src.services.people import agent_service, party_service  # noqa: E402

AGENTS = [
    {"AgentName": "Rohit Sharma", "mobile": "9876543210", "email": "rohit@example.com"},
    {"AgentName": "Amit Verma", "mobile": "9876543211", "email": "amit@example.com"},
    {"AgentName": "Suresh Kumar", "mobile": "9876543212"},
]

ITEMS = [
    {"name": "Scaffolding Pipe", "description": "Steel scaffolding pipe, 10ft", "qty": 100,
     "rent": 25.0, "rentFrequency": "daily", "materialType": "Steel"},
    {"name": "Wheel Barrow", "description": "Construction wheel barrow", "qty": 30,
     "rent": 60.0, "rentFrequency": "daily", "materialType": "Iron"},
    {"name": "Concrete Mixer", "description": "Electric concrete mixer, 500L", "qty": 10,
     "rent": 900.0, "rentFrequency": "daily", "materialType": "Steel"},
    {"name": "Aluminium Ladder", "description": "12ft foldable ladder", "qty": 40,
     "rent": 80.0, "rentFrequency": "daily", "materialType": "Aluminium"},
    {"name": "Drill Machine", "description": "Corded electric drill", "qty": 25,
     "rent": 150.0, "rentFrequency": "daily", "materialType": "Metal"},
    {"name": "Diesel Generator", "description": "5 KVA diesel generator", "qty": 8,
     "rent": 2500.0, "rentFrequency": "daily", "materialType": "Steel"},
    {"name": "Water Pump", "description": "Single-phase industrial pump", "qty": 15,
     "rent": 300.0, "rentFrequency": "daily", "materialType": "Iron"},
    {"name": "Mini Road Roller", "description": "Hydraulic mini roller", "qty": 4,
     "rent": 4500.0, "rentFrequency": "daily", "materialType": "Steel"},
]

PARTIES = [
    {"id": "CUST001", "name": "Sharma Constructions", "mobile": "9123456780",
     "address": "12 MG Road, Pune"},
    {"id": "CUST002", "name": "Verma Builders", "mobile": "9123456781",
     "address": "44 Station Road, Nashik"},
    {"id": "CUST003", "name": "Patil Infra", "mobile": "9123456782",
     "address": "7 Ring Road, Nagpur"},
    {"id": "CUST004", "name": "Deshmukh Contractors", "mobile": "9123456783"},
]

BUSINESS_TABLES = [
    ReturnTxn, Payment, ContractLine, RentalContract,
    RentalPrice, AvailableStock, Item, Party, Agent,
]


def reset(db) -> None:
    # Deleted in FK-dependency order; the ledger references parties and items
    # with ondelete=RESTRICT, so children must go first.
    for model in BUSINESS_TABLES:
        db.query(model).delete()
    db.commit()
    print("Cleared existing business data.")


def seed(db) -> None:
    now = datetime.now(UTC)

    agents = [agent_service.create(db, obj_in=AgentCreate(**a)) for a in AGENTS]
    print(f"Created {len(agents)} agents.")

    items = [item_service.create(db, obj_in=ItemCreate(**i)) for i in ITEMS]
    print(f"Created {len(items)} items with stock and rates.")

    parties = [party_service.create(db, obj_in=PartyCreate(**p)) for p in PARTIES]
    print(f"Created {len(parties)} parties.")

    # A closed rental from three weeks ago, fully returned and paid.
    closed = txn_svc.create_contract(db, obj_in=ContractCreate(
        partyId="CUST001", agentId=agents[0].agentId,
        startDate=now - timedelta(days=21),
        expectedReturnDate=now - timedelta(days=14),
        advancePaid=5000.0,
        items=[ContractLineIn(itemId=items[0].itemId, qty=40),
               ContractLineIn(itemId=items[3].itemId, qty=4)],
        notes="Site A — first floor slab.",
    ))
    result = txn_svc.process_return(db, contract_id=closed.contractId, obj_in=ReturnCreate(
        items=[{"lineId": line.id, "qty": line.qty} for line in closed.lines],
        returnDate=now - timedelta(days=14),
        amountPaid=9000.0,
    ))
    print(f"Closed contract {closed.contractNo}: charged {result['totalCharged']:.2f}")

    # A partly-returned rental still running.
    partial = txn_svc.create_contract(db, obj_in=ContractCreate(
        partyId="CUST002", agentId=agents[1].agentId,
        startDate=now - timedelta(days=9),
        expectedReturnDate=now + timedelta(days=5),
        advancePaid=3000.0,
        items=[ContractLineIn(itemId=items[2].itemId, qty=2),
               ContractLineIn(itemId=items[4].itemId, qty=5)],
    ))
    txn_svc.process_return(db, contract_id=partial.contractId, obj_in=ReturnCreate(
        items=[{"lineId": partial.lines[1].id, "qty": 2}],
        returnDate=now - timedelta(days=2),
        amountPaid=0.0,
    ))
    print(f"Partly-returned contract {partial.contractNo}")

    # An overdue rental — expected back three days ago, nothing returned.
    overdue = txn_svc.create_contract(db, obj_in=ContractCreate(
        partyId="CUST003", agentId=agents[2].agentId,
        startDate=now - timedelta(days=17),
        expectedReturnDate=now - timedelta(days=3),
        items=[ContractLineIn(itemId=items[5].itemId, qty=1)],
        notes="Chase for return.",
    ))
    print(f"Overdue contract {overdue.contractNo}")

    # A fresh rental opened today.
    fresh = txn_svc.create_contract(db, obj_in=ContractCreate(
        partyId="CUST004",
        startDate=now,
        expectedReturnDate=now + timedelta(days=10),
        advancePaid=1000.0,
        items=[ContractLineIn(itemId=items[6].itemId, qty=3),
               ContractLineIn(itemId=items[1].itemId, qty=6)],
    ))
    print(f"Open contract {fresh.contractNo}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="Delete existing business data first")
    parser.add_argument("--force", action="store_true", help="Allow running against production")
    parser.add_argument("--admin", metavar="USER:PASS", help="Also create an admin login")
    args = parser.parse_args()

    if settings.is_production and not args.force:
        print(
            f"Refusing to seed: ENVIRONMENT={settings.ENVIRONMENT}. "
            "Pass --force if you really mean it.",
            file=sys.stderr,
        )
        return 1

    print(f"Target: {settings.DATABASE_URL.split('@')[-1]}")

    if settings.DATABASE_URL.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if args.reset:
            reset(db)

        if args.admin:
            username, _, password = args.admin.partition(":")
            if not db.query(User).filter(User.username == username).first():
                db.add(User(
                    username=username,
                    hashed_password=hash_password(password),
                    is_superuser=True,
                ))
                db.commit()
                print(f"Created admin user {username!r}.")

        seed(db)
        print("\nDone.")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"Seeding failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
