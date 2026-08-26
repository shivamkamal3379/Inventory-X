# Architecture

## Layout

```
Backend/
  src/
    core/        config, database, security, middleware, rate limiting, errors
    models/      SQLAlchemy tables
    schemas/     Pydantic request/response contracts
    services/    business logic — billing, contracts, CRUD
    routers/     HTTP endpoints (thin; they validate and delegate)
  alembic/       migrations
  scripts/       seed_demo.py and other ops tasks
  tests/         pytest suite
Frontend/
  src/
    components/  ui/ primitives, providers (theme, toasts, error boundary)
    hooks/       useAsync, useDebounced
    layouts/     auth and dashboard shells
    pages/       one file per route
    services/    apiClient, auth, db (typed API surface)
```

The dependency direction is one-way: `routers → services → models`. A router never
contains business logic, and a service never knows about HTTP. That is why the billing
rules can be unit-tested without a database or a request.

## Data model

```
users                                    login accounts

t_Agents ──┐
           ├── t_party ─────┐            customer, balance, activeItems
           │                │
t_Item ────┼── t_AvaiableStock           qty / RentedOutQty / availableQty
           └── RentalPrice               rate + frequency
                            │
              rentalContract ┤           the invoice: party, dates, advance, totals
                    │        │
              contractLine   │           one row per item: qty, returnedQty, rate
                    │        │
                 returnTxn ──┘           per-return: days held, periods, charge
                  payment                money against a contract
```

Table names are inherited from the original ERD, including the misspelled
`t_AvaiableStock`. They are left alone deliberately: renaming them buys nothing and
would invalidate any existing deployment's data.

### Invariants enforced by the database, not just code

- `availableQty + RentedOutQty = qty` — a `CHECK` constraint on the stock table. If
  application logic ever gets this wrong, the write fails rather than corrupting stock.
- `returnedQty <= qty` on every contract line.
- Quantities and money are non-negative.
- Ledger rows reference parties and items with `ON DELETE RESTRICT`, so deleting a
  customer or an item can never silently erase rental history.
- Stock and price rows cascade from their item, so deleting an item leaves no orphans.

## Request lifecycle

```
nginx ──► SecurityHeaders ──► RequestContext ──► CORS ──► auth dep ──► router
                                    │                                     │
                              request id +                            service
                              access log                                  │
                                                                     PostgreSQL
```

`RequestContextMiddleware` assigns an id per request, stores it in a `ContextVar`, logs
one structured line with method/path/status/duration, and returns it as `X-Request-ID`.
Every log line from that request carries the same id, so a user-reported failure is
one `grep` away.

All exceptions funnel through handlers in `core/errors.py`, so a client always receives
`{"detail": ..., "request_id": ...}` — never a stack trace and never a raw driver
message that would leak table names.

## Decisions worth knowing

**Auth is attached at router-inclusion time**, not per endpoint:

```python
for router in protected:
    app.include_router(router, dependencies=[CurrentUser])
```

A newly added route is therefore protected by default. The previous code annotated
nothing, and every CRUD endpoint was publicly readable and writable.

**Prices are never accepted from the client.** `POST /contracts/` takes items and
quantities; the rate comes from `RentalPrice` server-side and is copied onto the
contract line. A crafted request cannot alter what someone is charged, and a later
price change cannot rewrite an issued bill.

**Stock is locked before it is read.** `db.get(AvailableStock, id, with_for_update=True)`
holds the row for the transaction. Without it, concurrent rentals each read the same
availability and all pass the check — `tests/test_concurrency.py` demonstrates exactly
that, and fails if the lock is removed.

**Every write that spans tables commits once.** Creating a contract touches stock, the
party ledger and the contract itself; the service flushes to obtain ids but commits a
single time at the end, so a failure part-way leaves nothing behind.

**Timestamps are aware UTC everywhere in Python.** PostgreSQL returns
timezone-aware datetimes and SQLite returns naive ones. Everything passes through
`billing.as_utc()`, which treats naive values as UTC. This is not
`astimezone(tz=None)` — that converts to the *server's local* zone and shifted every
rental duration by the host's UTC offset, producing off-by-one-day bills that appeared
only on PostgreSQL.

**Migrations own the schema.** `create_all()` runs only for SQLite (local runs and
tests). In Docker the entrypoint runs `alembic upgrade head` before the server starts,
and CI fails the build if the models have drifted from the migrations.

## Frontend

`services/db.js` is the single place that knows API shapes; pages never call axios
directly. `useAsync` tracks `{data, loading, error}` and ignores superseded responses,
so a slow search cannot land after a faster newer one and overwrite it.

Failures surface as toasts and inline `ErrorState` blocks with a retry. Every list
distinguishes *loading*, *empty*, and *failed* — previously all three rendered as an
empty table.

Theme tokens are HSL triplets in `index.css` exposed to Tailwind via `@theme inline`.
Charts are inline SVG with no charting dependency; each is single-series, so it carries
no legend, and each exposes its numbers as a screen-reader table.
