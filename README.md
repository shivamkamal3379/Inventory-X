# Inventory X

Rental inventory management for equipment-hire businesses: track stock, rent it out
on a contract, take it back with the bill calculated from how long it was held, and
keep every customer balance straight.

- **Backend** — FastAPI · SQLAlchemy 2 · PostgreSQL · Alembic
- **Frontend** — React 19 · Vite · Tailwind CSS 4
- **Deployment** — Docker Compose (PostgreSQL + API + nginx-served SPA)

---

## Quick start

```bash
cp .env.example .env
```

Fill in the three required values (`POSTGRES_PASSWORD`, `SECRET_KEY`,
`FIRST_ADMIN_PASSWORD`), then:

```bash
docker compose up -d --build
```

The app is at **http://localhost:8080**. Sign in with the `FIRST_ADMIN_USERNAME` /
`FIRST_ADMIN_PASSWORD` you set — the backend creates that account on first boot, so
registration can stay closed.

To load demo data (four customers, eight items, and rentals in every state):

```bash
docker compose exec api python scripts/seed_demo.py --reset --force
```

---

## How the domain works

**A rental is a contract, not a row per item.** One `POST /contracts/` carries every
item going out, under one invoice number (`INV-000001`). That is what makes a
printable bill, a single return, and duration-based billing possible.

**Rent accrues on return, not at pickup.** The amount depends on how long the goods
were actually held, which is unknown when they leave. So:

| Event | What happens to the ledger |
|---|---|
| Contract created | Stock reserved. Advance (if any) posts as a **credit** to the party. No rent charged yet. |
| Items returned | Stock restored. `rate × qty × periods held` posts as a **debit**. Any payment taken reduces it. |
| Payment recorded | Reduces the party's balance. |

A positive party balance means they owe you; negative means you are holding their
money.

**Billing rules** (`Backend/src/services/billing.py`, unit-tested in isolation):

- Duration is counted in whole days between pickup and return.
- A same-day return still costs one period — no rental shop bills zero.
- Part periods round up: on a weekly rate, 8 days is 2 weeks.
- The rate is the one recorded on the contract line at pickup, so changing your
  price list never rewrites a bill you already issued.

**Stock cannot go negative.** Availability is read under a row lock
(`SELECT … FOR UPDATE`), so two people writing rentals at the same moment cannot
both pass the availability check. There is a test that proves it: remove the lock
and 20 concurrent requests all succeed against 5 units.

---

## API

Every endpoint except `/health`, `/ready` and `/auth/*` requires
`Authorization: Bearer <token>`.

| Area | Endpoints |
|---|---|
| Auth | `POST /auth/login` · `POST /auth/register` · `GET /auth/me` · `POST /auth/change-password` |
| Items | `GET POST /items/` · `GET PUT DELETE /items/{id}` · `GET PUT /items/{id}/stock` |
| Prices | `GET POST /prices/` · `GET PUT DELETE /prices/{itemId}` |
| Parties | `GET POST /parties/` · `GET PUT DELETE /parties/{id}` · `GET /parties/{id}/ledger` |
| Agents | `GET POST /agents/` · `GET PUT DELETE /agents/{id}` |
| Contracts | `GET POST /contracts/` · `GET /contracts/{id}` · `GET /contracts/{id}/quote` · `POST /contracts/{id}/return` · `POST /contracts/{id}/payment` |
| History | `GET /returns/` · `GET /payments/` |
| Dashboard | `GET /dashboard/stats` · `/activity` · `/trend` · `/top-items` |

`GET /contracts/{id}/quote` prices a return **without committing it**, so the counter
can show the customer the amount first. It runs the same calculation the commit does.

Interactive docs are at `/api/docs` — served in development only, and disabled when
`ENVIRONMENT=production`.

---

## Local development

Requires Python 3.13+ and Node 22+.

```bash
make setup      # backend venv + npm install
make dev-api    # API on :8000 (SQLite, no Postgres needed)
make dev-web    # Vite on :5173, proxying /api to :8000
```

`make help` lists everything. Common targets:

```bash
make test       # backend suite on SQLite
make test-pg    # same suite on PostgreSQL — what CI runs
make lint       # ruff + eslint
make migration m="add x"   # autogenerate a migration
```

SQLite is fine for local work, but **run `make test-pg` before trusting a change to
dates or money**: SQLite returns naive datetimes and PostgreSQL returns aware ones,
and that difference has already hidden a real billing bug.

---

## Configuration

All settings are environment variables; see `.env.example` for the annotated list.

The app **refuses to start** when `ENVIRONMENT` is `staging` or `production` and any
of these hold:

- `SECRET_KEY` is the development default or shorter than 32 characters
- `CORS_ORIGINS` contains `*`
- `DATABASE_URL` points at SQLite
- `DEBUG` is true

That is deliberate. A misconfigured deployment should fail loudly at boot rather than
quietly serve traffic with forgeable tokens.

---

## Documentation

| Document | Contents |
|---|---|
| [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deploying to a VPS, TLS, backups, upgrades, troubleshooting |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layout, data model, request lifecycle, design decisions |
| [CHANGELOG.md](CHANGELOG.md) | What changed in the 1.0 hardening pass, and why |

---

## Tests

126 tests covering authentication and access control, the billing rules, the contract
lifecycle, stock invariants, and concurrent oversell prevention.

```bash
cd Backend && pytest
```

CI runs the suite against PostgreSQL, checks that migrations apply cleanly to an empty
database, verifies the models have not drifted from the migrations, and boots the full
Docker stack to smoke-test it through nginx.
