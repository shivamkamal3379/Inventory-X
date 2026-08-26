"""Rental contract lifecycle: create, return, pay.

Every method here touches stock, the party ledger and the contract together, so
each one runs as a single transaction and commits exactly once. Stock rows are
locked FOR UPDATE before availability is read, which is what stops two
concurrent rentals from both passing the check and overselling. On SQLite the
lock clause is a no-op and safety comes from its single-writer lock instead.
"""

import logging
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session, selectinload

from src.models.inventory import AvailableStock, Item, RentalPrice
from src.models.people import Agent, Party, PartyStatus
from src.models.transactions import (
    ContractLine,
    ContractStatus,
    Payment,
    RentalContract,
    RentFrequency,
    ReturnTxn,
)
from src.schemas.transactions import ContractCreate, PaymentCreate, ReturnCreate
from src.services.billing import as_utc, compute_charge
from src.services.numbering import format_contract_no

logger = logging.getLogger("inventoryx.contracts")


# --------------------------------------------------------------------------- #
# Party ledger
# --------------------------------------------------------------------------- #


def recalculate_party_status(party: Party) -> None:
    """Derive party status from balance and items held.

    Precedence: a manual DEFAULT flag wins over everything; then an outstanding
    balance; then items still out; otherwise the account is settled.

    This differs from the original ordering, which checked activeItems first and
    so labelled a party who owed money but held items as ACTIVE, hiding the debt.
    Its `else: INACTIVE` branch was also unreachable. INACTIVE is now reserved
    for accounts set that way by hand.
    """
    if party.status == PartyStatus.DEFAULT:
        return

    balance = round(party.balance or 0.0, 2)
    active_items = party.activeItems or 0

    if balance > 0:
        party.status = PartyStatus.PAYMENT_DUE
    elif active_items > 0:
        party.status = PartyStatus.ACTIVE
    else:
        party.status = PartyStatus.CLOSED


def _apply_to_balance(party: Party, delta: float) -> None:
    """Positive delta = party owes more; negative = party owes less."""
    party.balance = round((party.balance or 0.0) + delta, 2)


# --------------------------------------------------------------------------- #
# Loading helpers
# --------------------------------------------------------------------------- #


def _now() -> datetime:
    """Aware UTC. Everything this app writes is UTC; see billing.as_utc."""
    return datetime.now(UTC)


def _load_party(db: Session, party_id: str) -> Party:
    party = db.get(Party, party_id, with_for_update=True)
    if party is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Party {party_id} not found"
        )
    return party


def _load_locked_stock(db: Session, item_id: int) -> AvailableStock:
    stock = db.get(AvailableStock, item_id, with_for_update=True)
    if stock is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No stock record for item {item_id}",
        )
    return stock


def _load_contract(db: Session, contract_id: int, *, lock: bool = False) -> RentalContract:
    stmt = (
        select(RentalContract)
        .options(selectinload(RentalContract.lines))
        .where(RentalContract.contractId == contract_id)
    )
    if lock:
        stmt = stmt.with_for_update(of=RentalContract)
    contract = db.execute(stmt).scalars().first()
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Contract {contract_id} not found"
        )
    return contract


def _refresh_contract_status(contract: RentalContract) -> None:
    outstanding = sum(line.outstandingQty for line in contract.lines)
    total = sum(line.qty for line in contract.lines)

    if outstanding == 0:
        contract.status = ContractStatus.CLOSED
        contract.closedAt = contract.closedAt or _now()
    elif outstanding < total:
        contract.status = ContractStatus.PARTIAL
        contract.closedAt = None
    else:
        contract.status = ContractStatus.OPEN
        contract.closedAt = None


# --------------------------------------------------------------------------- #
# Contract creation
# --------------------------------------------------------------------------- #


def create_contract(db: Session, *, obj_in: ContractCreate) -> RentalContract:
    party = _load_party(db, obj_in.partyId)

    agent_name = None
    if obj_in.agentId is not None:
        agent = db.get(Agent, obj_in.agentId)
        if agent is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent {obj_in.agentId} not found",
            )
        agent_name = agent.AgentName

    start = obj_in.startDate or _now()
    if obj_in.expectedReturnDate and as_utc(obj_in.expectedReturnDate) < as_utc(start):
        raise HTTPException(
            status_code=422,  # renamed across Starlette versions; the literal is stable
            detail="Expected return date cannot be before the start date.",
        )

    contract = RentalContract(
        contractNo="",  # replaced below once the id is assigned
        partyId=party.id,
        PartyName=party.name,
        agentId=obj_in.agentId,
        AgentName=agent_name,
        status=ContractStatus.OPEN,
        startDate=start,
        expectedReturnDate=obj_in.expectedReturnDate,
        advancePaid=obj_in.advancePaid,
        accruedRent=0.0,
        totalPaid=0.0,
        notes=obj_in.notes,
    )
    db.add(contract)
    db.flush()  # assigns contractId without ending the transaction
    contract.contractNo = format_contract_no(contract.contractId)

    total_units = 0
    for line_in in obj_in.items:
        item = db.get(Item, line_in.itemId)
        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item {line_in.itemId} not found",
            )

        stock = _load_locked_stock(db, line_in.itemId)
        if stock.availableQty < line_in.qty:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock for '{item.name}'. "
                    f"Available: {stock.availableQty}, requested: {line_in.qty}"
                ),
            )

        price = db.get(RentalPrice, line_in.itemId)
        rate = price.rent if price is not None else 0.0
        frequency = (
            line_in.rentFrequency.value
            if line_in.rentFrequency
            else (
                price.rentFrequency if price and price.rentFrequency else RentFrequency.DAILY.value
            )
        )

        stock.availableQty -= line_in.qty
        stock.RentedOutQty += line_in.qty
        db.add(stock)

        db.add(
            ContractLine(
                contractId=contract.contractId,
                itemId=item.itemId,
                Item=item.name,
                qty=line_in.qty,
                returnedQty=0,
                ratePerUnit=rate,
                rentFrequency=frequency,
                accruedRent=0.0,
            )
        )
        total_units += line_in.qty

    # An advance is money in hand before any rent has accrued, so it sits as a
    # credit against the party until returns start charging rent.
    if obj_in.advancePaid:
        _apply_to_balance(party, -obj_in.advancePaid)

    party.activeItems = (party.activeItems or 0) + total_units
    recalculate_party_status(party)
    db.add(party)

    db.commit()
    db.refresh(contract)
    logger.info(
        "contract_created no=%s party=%s units=%s advance=%s",
        contract.contractNo,
        party.id,
        total_units,
        obj_in.advancePaid,
    )
    return contract


# --------------------------------------------------------------------------- #
# Returns
# --------------------------------------------------------------------------- #


def quote_return(db: Session, *, contract_id: int, as_of: datetime | None = None) -> dict:
    """Price a full return of everything still out, without changing anything.

    Lets the UI show the customer their bill before the return is committed.
    """
    contract = _load_contract(db, contract_id)
    as_of = as_of or _now()

    lines, subtotal = [], 0.0
    for line in contract.lines:
        if line.outstandingQty <= 0:
            continue
        breakdown = compute_charge(
            start=contract.startDate,
            end=as_of,
            qty=line.outstandingQty,
            rate_per_unit=line.ratePerUnit,
            frequency=line.rentFrequency,
        )
        subtotal += breakdown.rentCharged
        lines.append(
            {
                "lineId": line.id,
                "itemId": line.itemId,
                "Item": line.Item,
                "qty": line.outstandingQty,
                "ratePerUnit": line.ratePerUnit,
                "rentFrequency": line.rentFrequency,
                "daysHeld": breakdown.daysHeld,
                "periodsCharged": breakdown.periodsCharged,
                "rentCharged": breakdown.rentCharged,
            }
        )

    subtotal = round(subtotal, 2)
    return {
        "contractId": contract.contractId,
        "contractNo": contract.contractNo,
        "asOf": as_of,
        "lines": lines,
        "subtotal": subtotal,
        "advanceApplied": contract.advancePaid,
        "alreadyPaid": contract.totalPaid,
        "netDue": round(
            subtotal + contract.accruedRent - contract.totalPaid - contract.advancePaid, 2
        ),
    }


def process_return(db: Session, *, contract_id: int, obj_in: ReturnCreate) -> dict:
    contract = _load_contract(db, contract_id, lock=True)
    if contract.status == ContractStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contract is cancelled.")

    return_date = obj_in.returnDate or _now()
    # Compare in a single representation: the client may send an aware datetime
    # while SQLite hands back a naive one, and subtracting the two raises.
    if as_utc(return_date) < as_utc(contract.startDate):
        raise HTTPException(
            status_code=422,  # renamed across Starlette versions; the literal is stable
            detail="Return date cannot be before the contract start date.",
        )

    party = _load_party(db, contract.partyId)
    lines_by_id = {line.id: line for line in contract.lines}

    receipts: list[ReturnTxn] = []
    total_charged = 0.0

    for req in obj_in.items:
        line = lines_by_id.get(req.lineId)
        if line is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Line {req.lineId} is not part of contract {contract.contractNo}.",
            )
        if req.qty > line.outstandingQty:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Cannot return {req.qty} x '{line.Item}': only "
                    f"{line.outstandingQty} still out on this contract."
                ),
            )

        breakdown = compute_charge(
            start=contract.startDate,
            end=return_date,
            qty=req.qty,
            rate_per_unit=line.ratePerUnit,
            frequency=line.rentFrequency,
        )

        stock = _load_locked_stock(db, line.itemId)
        stock.availableQty += req.qty
        stock.RentedOutQty -= req.qty
        db.add(stock)

        line.returnedQty += req.qty
        line.accruedRent = round(line.accruedRent + breakdown.rentCharged, 2)
        db.add(line)

        receipt = ReturnTxn(
            contractId=contract.contractId,
            lineId=line.id,
            partyId=contract.partyId,
            PartyName=contract.PartyName,
            itemId=line.itemId,
            Item=line.Item,
            qty=req.qty,
            returnDate=return_date,
            daysHeld=breakdown.daysHeld,
            periodsCharged=breakdown.periodsCharged,
            ratePerUnit=line.ratePerUnit,
            rentCharged=breakdown.rentCharged,
            amountPaid=0.0,  # payment is applied once, below, across the whole return
        )
        db.add(receipt)
        receipts.append(receipt)

        total_charged += breakdown.rentCharged
        party.activeItems = max(0, (party.activeItems or 0) - req.qty)

    total_charged = round(total_charged, 2)

    if receipts:
        receipts[0].amountPaid = obj_in.amountPaid

    contract.accruedRent = round(contract.accruedRent + total_charged, 2)
    contract.totalPaid = round(contract.totalPaid + obj_in.amountPaid, 2)
    if obj_in.notes:
        contract.notes = f"{contract.notes}\n{obj_in.notes}" if contract.notes else obj_in.notes

    _refresh_contract_status(contract)
    db.add(contract)

    # Rent becomes owed now; any payment taken at the counter reduces it.
    _apply_to_balance(party, total_charged - obj_in.amountPaid)
    recalculate_party_status(party)
    db.add(party)

    db.commit()
    db.refresh(contract)
    logger.info(
        "return_processed contract=%s charged=%s paid=%s",
        contract.contractNo,
        total_charged,
        obj_in.amountPaid,
    )
    return {
        "returns": receipts,
        "totalCharged": total_charged,
        "totalPaid": obj_in.amountPaid,
        "contract": contract,
    }


# --------------------------------------------------------------------------- #
# Payments
# --------------------------------------------------------------------------- #


def record_payment(db: Session, *, contract_id: int, obj_in: PaymentCreate) -> Payment:
    contract = _load_contract(db, contract_id, lock=True)
    party = _load_party(db, contract.partyId)

    payment = Payment(
        contractId=contract.contractId,
        partyId=contract.partyId,
        amount=obj_in.amount,
        method=obj_in.method,
        notes=obj_in.notes,
    )
    db.add(payment)

    contract.totalPaid = round(contract.totalPaid + obj_in.amount, 2)
    db.add(contract)

    _apply_to_balance(party, -obj_in.amount)
    recalculate_party_status(party)
    db.add(party)

    db.commit()
    db.refresh(payment)
    logger.info("payment contract=%s amount=%s", contract.contractNo, obj_in.amount)
    return payment


# --------------------------------------------------------------------------- #
# Queries
# --------------------------------------------------------------------------- #


def get_contract(db: Session, contract_id: int) -> RentalContract:
    return _load_contract(db, contract_id)


def list_contracts(
    db: Session,
    *,
    party_id: str | None = None,
    contract_status: str | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[RentalContract]:
    stmt = select(RentalContract).options(selectinload(RentalContract.lines))
    if party_id:
        stmt = stmt.where(RentalContract.partyId == party_id)
    if contract_status:
        stmt = stmt.where(RentalContract.status == contract_status)
    if q:
        term = f"%{q.lower()}%"
        stmt = stmt.where(
            func.lower(RentalContract.contractNo).like(term)
            | func.lower(func.coalesce(RentalContract.PartyName, "")).like(term)
        )
    stmt = stmt.order_by(desc(RentalContract.startDate), desc(RentalContract.contractId))
    stmt = stmt.offset(skip).limit(limit)
    return list(db.execute(stmt).scalars().all())


def list_returns(
    db: Session, *, party_id: str | None = None, skip: int = 0, limit: int = 50
) -> list[ReturnTxn]:
    stmt = select(ReturnTxn)
    if party_id:
        stmt = stmt.where(ReturnTxn.partyId == party_id)
    stmt = stmt.order_by(desc(ReturnTxn.returnDate), desc(ReturnTxn.id))
    return list(db.execute(stmt.offset(skip).limit(limit)).scalars().all())


def list_payments(
    db: Session, *, party_id: str | None = None, skip: int = 0, limit: int = 50
) -> list[Payment]:
    stmt = select(Payment)
    if party_id:
        stmt = stmt.where(Payment.partyId == party_id)
    stmt = stmt.order_by(desc(Payment.paidAt), desc(Payment.id))
    return list(db.execute(stmt.offset(skip).limit(limit)).scalars().all())


def contract_summary(contract: RentalContract) -> dict:
    return {
        "contractId": contract.contractId,
        "contractNo": contract.contractNo,
        "partyId": contract.partyId,
        "PartyName": contract.PartyName,
        "AgentName": contract.AgentName,
        "status": contract.status,
        "startDate": contract.startDate,
        "expectedReturnDate": contract.expectedReturnDate,
        "advancePaid": contract.advancePaid,
        "accruedRent": contract.accruedRent,
        "totalPaid": contract.totalPaid,
        "balanceDue": contract.balanceDue,
        "itemCount": len(contract.lines),
        "outstandingQty": sum(line.outstandingQty for line in contract.lines),
    }
