"""Rental duration and charge calculation.

Deliberately pure: no database, no ORM objects. The rules a business argues
about live here and are unit-tested directly.

Rules
-----
* Duration is counted in whole days between pickup and return.
* A same-day return still costs one billing period — the goods were unavailable
  for that day, and no rental shop bills zero.
* Part-periods round up: on a weekly rate, 8 days is 2 weeks. This is the normal
  convention for rental hire and must be stated on the invoice.
* The rate is whatever was recorded on the contract line at pickup, never the
  current price list, so a later price change cannot retroactively rewrite a bill.
"""

import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.models.transactions import PERIOD_DAYS, RentFrequency

MAX_REASONABLE_DAYS = 3650  # 10 years; beyond this the dates are almost certainly wrong


@dataclass(frozen=True)
class ChargeBreakdown:
    daysHeld: int
    periodsCharged: int
    ratePerUnit: float
    qty: int
    rentCharged: float


def days_between(start: datetime, end: datetime) -> int:
    """Whole days from `start` to `end`, floored at 0."""
    delta: timedelta = as_utc(end) - as_utc(start)
    return max(0, delta.days)


def as_utc(value: datetime) -> datetime:
    """Return an aware UTC datetime.

    Postgres hands back timezone-aware values for `DateTime(timezone=True)`;
    SQLite hands back naive ones; a JSON client may send either. Mixing them in
    a subtraction raises, so every datetime is funnelled through here first.

    A naive value is assumed to already be UTC, which holds because everything
    written to the database goes through `_now()` or arrives as a client
    timestamp that this application defines as UTC.

    Note this is deliberately not `astimezone(tz=None)` — that converts to the
    *server's local* timezone, which silently shifted every rental duration by
    the local UTC offset and produced off-by-one-day bills.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def periods_for(days_held: int, frequency: str) -> int:
    """Number of billing periods to charge, minimum one."""
    period_days = PERIOD_DAYS.get(frequency, PERIOD_DAYS[RentFrequency.DAILY.value])
    if days_held <= 0:
        return 1
    return max(1, math.ceil(days_held / period_days))


def compute_charge(
    *,
    start: datetime,
    end: datetime,
    qty: int,
    rate_per_unit: float,
    frequency: str,
) -> ChargeBreakdown:
    """Charge for returning `qty` units held from `start` to `end`."""
    if qty <= 0:
        raise ValueError("qty must be positive")

    days_held = days_between(start, end)
    if days_held > MAX_REASONABLE_DAYS:
        raise ValueError(
            f"Rental duration of {days_held} days looks wrong — check the contract dates."
        )

    periods = periods_for(days_held, frequency)
    charged = round(rate_per_unit * qty * periods, 2)
    return ChargeBreakdown(
        daysHeld=days_held,
        periodsCharged=periods,
        ratePerUnit=rate_per_unit,
        qty=qty,
        rentCharged=charged,
    )
