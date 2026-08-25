"""Unit tests for the duration/charge rules. No database involved."""

from datetime import datetime, timedelta

import pytest

from src.services.billing import ChargeBreakdown, as_utc, compute_charge, days_between, periods_for

BASE = datetime(2026, 1, 1, 10, 0, 0)


@pytest.mark.parametrize(
    "end,expected",
    [
        (BASE, 0),
        (BASE + timedelta(hours=5), 0),
        (BASE + timedelta(days=1), 1),
        (BASE + timedelta(days=1, hours=23), 1),
        (BASE + timedelta(days=30), 30),
        (BASE - timedelta(days=5), 0),  # clamped, never negative
    ],
)
def test_days_between(end, expected):
    assert days_between(BASE, end) == expected


@pytest.mark.parametrize(
    "days,freq,expected",
    [
        (0, "daily", 1),  # same-day return still costs one period
        (1, "daily", 1),
        (7, "daily", 7),
        (0, "weekly", 1),
        (7, "weekly", 1),
        (8, "weekly", 2),  # part-periods round up
        (14, "weekly", 2),
        (0, "monthly", 1),
        (30, "monthly", 1),
        (31, "monthly", 2),
        (5, "unknown-frequency", 5),  # falls back to daily
    ],
)
def test_periods_for(days, freq, expected):
    assert periods_for(days, freq) == expected


def test_daily_charge_scales_with_days_and_qty():
    """The core fix: duration now affects the bill. Previously a 10-day rental
    cost exactly the same as a 1-day rental."""
    one_day = compute_charge(
        start=BASE, end=BASE + timedelta(days=1), qty=2, rate_per_unit=500.0, frequency="daily"
    )
    ten_days = compute_charge(
        start=BASE, end=BASE + timedelta(days=10), qty=2, rate_per_unit=500.0, frequency="daily"
    )
    assert one_day.rentCharged == 1000.0  # 500 x 2 x 1
    assert ten_days.rentCharged == 10000.0  # 500 x 2 x 10


def test_same_day_return_charges_one_period():
    c = compute_charge(
        start=BASE, end=BASE + timedelta(hours=3), qty=1, rate_per_unit=500.0, frequency="daily"
    )
    assert c.daysHeld == 0
    assert c.periodsCharged == 1
    assert c.rentCharged == 500.0


def test_weekly_rounds_up():
    c = compute_charge(
        start=BASE, end=BASE + timedelta(days=8), qty=1, rate_per_unit=1000.0, frequency="weekly"
    )
    assert c.periodsCharged == 2
    assert c.rentCharged == 2000.0


def test_zero_rate_is_allowed():
    c = compute_charge(
        start=BASE, end=BASE + timedelta(days=3), qty=4, rate_per_unit=0.0, frequency="daily"
    )
    assert c.rentCharged == 0.0


def test_aware_and_naive_datetimes_can_be_mixed():
    """SQLite returns naive datetimes while a JSON client may send an aware one;
    subtracting them directly would raise TypeError at billing time."""
    from datetime import UTC

    aware_end = datetime(2026, 1, 6, 10, 0, 0, tzinfo=UTC)
    c = compute_charge(start=BASE, end=aware_end, qty=1, rate_per_unit=100.0, frequency="daily")
    assert isinstance(c, ChargeBreakdown)
    assert c.rentCharged > 0


def test_absurd_duration_rejected():
    with pytest.raises(ValueError, match="looks wrong"):
        compute_charge(
            start=BASE,
            end=BASE + timedelta(days=40_000),
            qty=1,
            rate_per_unit=1.0,
            frequency="daily",
        )


def test_non_positive_qty_rejected():
    with pytest.raises(ValueError, match="qty must be positive"):
        compute_charge(
            start=BASE,
            end=BASE + timedelta(days=1),
            qty=0,
            rate_per_unit=1.0,
            frequency="daily",
        )


# --------------------------------------------------------------------------- #
# Timezone handling
# --------------------------------------------------------------------------- #


def test_as_utc_converts_rather_than_localises():
    """Regression: the original helper used astimezone(tz=None), which converts
    to the *server's local* timezone. On an IST host that shifted every stored
    UTC timestamp forward by 5h30m and produced off-by-one-day rental bills —
    a bug that only appeared on PostgreSQL, because SQLite returns naive
    datetimes and so never triggered the conversion.
    """
    from datetime import UTC, timezone

    aware = datetime(2026, 1, 1, 9, 0, 0, tzinfo=UTC)
    assert as_utc(aware) == aware
    assert as_utc(aware).hour == 9

    ist = timezone(timedelta(hours=5, minutes=30))
    assert as_utc(datetime(2026, 1, 1, 14, 30, 0, tzinfo=ist)) == aware

    naive = datetime(2026, 1, 1, 9, 0, 0)
    assert as_utc(naive) == aware  # naive is assumed to already be UTC


def test_duration_identical_whether_dates_are_aware_or_naive():
    """The same rental must bill the same amount on PostgreSQL (aware) and
    SQLite (naive), or the invoice depends on which database you deployed."""
    from datetime import UTC

    naive_start, naive_end = BASE, BASE + timedelta(days=5)
    aware_start = naive_start.replace(tzinfo=UTC)
    aware_end = naive_end.replace(tzinfo=UTC)

    kwargs = {"qty": 2, "rate_per_unit": 500.0, "frequency": "daily"}
    all_naive = compute_charge(start=naive_start, end=naive_end, **kwargs)
    all_aware = compute_charge(start=aware_start, end=aware_end, **kwargs)
    mixed = compute_charge(start=aware_start, end=naive_end, **kwargs)

    assert all_naive.rentCharged == all_aware.rentCharged == mixed.rentCharged == 5000.0
    assert all_naive.daysHeld == all_aware.daysHeld == mixed.daysHeld == 5
