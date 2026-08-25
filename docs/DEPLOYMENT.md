# Deployment

Deploying Inventory X to a single Linux server with Docker Compose.

The stack is three containers: PostgreSQL, the API, and nginx serving the built SPA
and proxying `/api` to the API. **Only nginx publishes a port** — the database and the
API are reachable only on the internal Docker network.

---

## 1. Requirements

- A Linux host with Docker Engine 24+ and the Compose plugin
- 1 GB RAM is enough for a small shop; 2 GB is comfortable
- A domain pointed at the server, if you want TLS (you do)

```bash
docker --version && docker compose version
```

---

## 2. Configure

```bash
git clone <your-repo-url> inventory-x
cd inventory-x
cp .env.example .env
```

Generate the two secrets:

```bash
openssl rand -base64 24                                        # POSTGRES_PASSWORD
python3 -c "import secrets; print(secrets.token_urlsafe(48))"  # SECRET_KEY
```

Edit `.env` and set, at minimum:

| Variable | Notes |
|---|---|
| `POSTGRES_PASSWORD` | Any strong value. Changing it later needs a database migration. |
| `SECRET_KEY` | ≥ 32 characters. **Changing it signs everyone out.** |
| `FIRST_ADMIN_USERNAME` / `FIRST_ADMIN_PASSWORD` | Creates your login on first boot. |
| `CORS_ORIGINS` | Your real origin, e.g. `https://rentals.example.com`. |
| `WEB_PORT` | Host port nginx binds. Keep `8080` and put a TLS proxy in front. |

Leave `ALLOW_REGISTRATION=false`. With it on, anyone who can reach the API can create
themselves a full-access account.

---

## 3. Launch

```bash
docker compose up -d --build
docker compose ps
```

Wait for all three to report `healthy`. The API container waits for PostgreSQL, runs
`alembic upgrade head`, creates the admin account if it does not exist, then starts
gunicorn. You never run migrations by hand for a normal deploy.

Verify:

```bash
curl -s localhost:8080/api/health
curl -s -o /dev/null -w '%{http_code}\n' localhost:8080/api/items/   # expect 401
```

A `401` there is the correct answer — it means authentication is enforced.

---

## 4. TLS

The stack serves plain HTTP on `WEB_PORT`. Terminate TLS in front of it. With Caddy,
the whole configuration is:

```caddyfile
rentals.example.com {
    reverse_proxy localhost:8080
}
```

Caddy obtains and renews the certificate automatically. With nginx or Traefik on the
host, proxy to `localhost:8080` and make sure `X-Forwarded-For` is set — the API
rate-limits logins on that header.

Then set `CORS_ORIGINS=https://rentals.example.com` in `.env` and
`docker compose up -d api`.

> **Do not expose the API container directly.** It trusts `X-Forwarded-For` because
> the documented topology always has a proxy in front that overwrites it. Exposed
> directly, a client could spoof the header and evade the login rate limit.

---

## 5. Backups

The database is the only stateful thing. Everything else rebuilds from the repo.

```bash
make backup     # writes backups/inventoryx-<timestamp>.sql.gz
```

Or directly:

```bash
docker compose exec -T db pg_dump -U inventoryx inventoryx | gzip > backup.sql.gz
```

Nightly, via the host's crontab:

```cron
0 2 * * * cd /srv/inventory-x && make backup && find backups -name '*.sql.gz' -mtime +30 -delete
```

Restore into an empty database:

```bash
docker compose down
docker volume rm inventoryx_db_data
docker compose up -d db
gunzip -c backup.sql.gz | docker compose exec -T db psql -U inventoryx inventoryx
docker compose up -d
```

**A backup you have never restored is not a backup.** Test the restore once.

---

## 6. Upgrading

```bash
git pull
docker compose up -d --build
```

Migrations run automatically as the API container starts. There is a short window
where old and new containers overlap; for a shop-hours deployment that is invisible.

To check what a migration will do before applying it:

```bash
docker compose run --rm api alembic upgrade head --sql
```

---

## 7. Operations

```bash
docker compose logs -f api          # follow API logs (JSON lines)
docker compose logs -f --tail=100   # everything
docker compose restart api
docker compose exec db psql -U inventoryx inventoryx
docker compose exec api python scripts/seed_demo.py --reset --force   # demo data
```

Logs are JSON when `LOG_JSON=true`, one object per line, each tagged with the
`request_id` that is also returned in the `X-Request-ID` response header. To trace a
failure a user reported, ask them for that header value and grep for it:

```bash
docker compose logs api | grep '<request-id>'
```

---

## 8. Scaling

`WEB_CONCURRENCY` sets gunicorn worker processes; `(2 × cores) + 1` is the usual rule.

**The login rate limiter counts per worker process.** It is a deliberately
dependency-free in-memory counter, so with `WEB_CONCURRENCY=4` the effective limit is
4 × `LOGIN_RATE_LIMIT_ATTEMPTS`. For a single shop that is fine. If you put this behind
a public login page at scale, move the limiter to Redis
(`Backend/src/core/rate_limit.py` is the only file that changes).

Running more than one *replica* of the API container has the same caveat, and nothing
else — the app holds no other in-process state and PostgreSQL handles the locking.

---

## 9. Troubleshooting

**API restarts in a loop.** Read the logs first:

```bash
docker compose logs api --tail=50
```

A `ValueError` at startup mentioning `SECRET_KEY`, `CORS_ORIGINS`, `DEBUG` or SQLite is
the configuration guard doing its job. Fix `.env` and `docker compose up -d api`.

**`Database temporarily unavailable` (503).** PostgreSQL is down or unreachable:

```bash
docker compose ps db
docker compose logs db --tail=50
```

**Login always fails.** If you changed `SECRET_KEY`, every existing token is invalid —
sign in again. If the admin account was never created, `FIRST_ADMIN_PASSWORD` was
probably blank at first boot; set it and restart the API, or create the user directly:

```bash
docker compose exec api python -c "
from src.core.database import SessionLocal
from src.core.security import hash_password
from src.models.auth import User
db = SessionLocal()
db.add(User(username='admin', hashed_password=hash_password('<new-password>'), is_superuser=True))
db.commit()
"
```

**Frontend calls the wrong API URL.** `VITE_API_BASE_URL` is inlined at *build* time,
not read at runtime. Changing it requires `docker compose build web`.

**Blank page after deploying.** A stale `index.html` referencing asset hashes that no
longer exist. nginx sends `no-cache` for `index.html` specifically to prevent this; if
it happens anyway, a hard reload clears it.
