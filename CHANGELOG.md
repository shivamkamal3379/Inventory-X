# Changelog

## 1.0.0 — production hardening

The application was reworked from a prototype into something deployable. The domain
model changed, so this is not a drop-in upgrade of an existing deployment.

### Fixed — correctness

- **`POST /items/` returned 500 on every call.** The schema field was `manufactureYr`
  and the model column `ManufactureYr`, so constructing the row raised `TypeError`
  before it reached the database. Nothing could be added to inventory, which meant the
  rental flow had never worked end to end.
- **Every endpoint except `/auth/*` was unauthenticated.** Items, parties, agents,
  rentals and dashboard statistics were all readable and writable with no token.
- **Party balances were always ₹0.** `rentAmount` was accepted from the request body
  and the frontend never sent it, so no rental ever charged anything.
- **Returning more than was rented inflated stock.** Returning 500 units of an item
  with 2 out set availability to 508 — stock created from nothing.
- **Negative quantities were accepted**, which *increased* available stock and
  *credited* the customer.
- **Concurrent rentals could oversell.** Availability was read without a lock, so
  simultaneous requests all passed the check. Now `SELECT … FOR UPDATE`; a test
  proves 20 concurrent requests against 5 units yield exactly 5 rentals.
- **Duplicate party IDs surfaced as an unhandled `IntegrityError` (500)** instead of a
  409.
- **`PUT /items/{id}` reset `created_at`** on every call, because the update schema
  carried a `default_factory` timestamp.
- **Updating an item's quantity did not update its stock row**, letting the two drift.
- **`/dashboard/activity` did not exist** although the dashboard called it, so "Recent
  activity" silently rendered empty.
- **Party status precedence hid debt.** A customer holding items *and* owing money was
  labelled `ACTIVE`; the `INACTIVE` branch was unreachable.
- **Deleting an item or party orphaned or erased ledger rows.**
- **Logout never cleared the token** — the handler was a `// TODO` followed by a
  redirect, so the next visit walked straight back in.
- **The auth guard only checked that a token string existed**, not that it was
  unexpired, so an expired session rendered the whole dashboard before every request
  401'd.
- **`Transactions.jsx` stored a Promise in React state**, and the page crashed on null
  descriptions and null balances.
- **Invoices printed `/dai`** — a string trim removed "ly" from "daily".

### Changed — domain model

- **A rental is now one contract with many items**, not one row per item. Previously a
  three-item rental became three unrelated ledger entries with no shared identifier, so
  it could never be printed as one bill or returned together.
- **Rent is billed by duration.** Previously a ₹500/day item cost ₹500 whether it was
  held one day or thirty. Rent now accrues on return as `rate × qty × periods held`,
  with same-day returns charged one period and part-periods rounded up.
- **Advances are held as a credit** against the party and offset against the final bill.
- Added `GET /contracts/{id}/quote` to price a return without committing it, and
  `POST /contracts/{id}/payment` to record payments.
- Removed `POST /rent/` and `POST /returns/`; `/returns/` and `/payments/` remain as
  read-only history.

### Added — infrastructure

- Alembic migrations; the schema is no longer created implicitly at import.
- Docker Compose stack: PostgreSQL, API, nginx-served SPA. Only nginx publishes a port.
- Multi-stage Dockerfiles, non-root runtime user, container healthchecks.
- Entrypoint that waits for the database and applies migrations before serving.
- CI: lint, format check, tests against PostgreSQL, migration-drift detection, and a
  full-stack smoke test through nginx.
- 126 tests: access control, billing rules, contract lifecycle, stock invariants,
  concurrency.
- Structured JSON logging with a request id propagated to `X-Request-ID`.
- Security headers, login rate limiting, and a uniform JSON error envelope.
- Startup guards that refuse to boot in production with a default `SECRET_KEY`,
  `CORS_ORIGINS=*`, `DEBUG=true`, or SQLite.

### Changed — dependencies and hygiene

- **`requirements.txt` was a UTF-16 `pip freeze` of the developer's whole machine** —
  190 packages including TensorFlow, PyTorch, Ultralytics, DeepFace and LangChain, none
  of which the project imports. Replaced with 15 actual dependencies.
- Removed the committed SQLite database and `__pycache__` directories from version
  control.
- CORS no longer allows all origins with credentials enabled.
- Removed manual test scripts targeting endpoints that no longer exist, and the SQL
  fixture that wrote rows without their stock records. Replaced by `scripts/seed_demo.py`.

### Changed — interface

Rebuilt on a token-based design system with light and dark themes, real loading /
empty / error states, toast notifications, accessible dialogs, and a printable invoice.
Added the Rentals, Contract detail, Party detail, Agents and Settings pages.

### Fixed — accessibility and layout

Found by auditing every page across light/dark and desktop/mobile, measuring
computed styles in the running app rather than reading the source:

- **Dropdown options were invisible in dark mode.** A native `<option>` is painted
  by the platform and does not inherit the parent `<select>`'s colours, so
  near-white text sat on the platform's white dropdown — a 1.06:1 ratio. Both
  colours are now set explicitly.
- **Party detail scrolled sideways on mobile.** Its tables had no scroll container,
  and the containing grid items lacked `min-w-0`, so a grid item refused to shrink
  below its content and pushed the whole page horizontally.
- Text contrast failed WCAG AA in several places and was corrected against measured
  ratios: light `--text-subtle` was 2.97:1, dark was 4.24:1, the dark brand used as
  link text was 4.23:1, and the status badges ran 3.0-3.3:1 at 11px. The chart
  colour was re-validated against the visualization colour spec after the change.
- Table-row links and the dashboard's "All rentals" link were 15-18px tall, below
  the 24px minimum for a reliable tap target.
- The back links on the detail pages wrapped an icon button with no accessible
  name, so a screen reader announced an unlabelled link.
