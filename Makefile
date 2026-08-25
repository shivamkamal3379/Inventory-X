# Common tasks. Run `make help` for the list.
.DEFAULT_GOAL := help
SHELL := /bin/bash

BACKEND := Backend
PY      := $(BACKEND)/.venv/bin/python

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-22s\033[0m %s\n", $$1, $$2}'

# --- Local development ------------------------------------------------------
.PHONY: setup
setup: ## Create the backend venv and install dev dependencies
	python3 -m venv $(BACKEND)/.venv || uv venv --python 3.13 $(BACKEND)/.venv
	$(BACKEND)/.venv/bin/pip install -r $(BACKEND)/requirements-dev.txt
	cd Frontend && npm install

.PHONY: dev-api
dev-api: ## Run the API locally with reload (SQLite)
	cd $(BACKEND) && .venv/bin/uvicorn src.main:app --reload --port 8000

.PHONY: dev-web
dev-web: ## Run the Vite dev server
	cd Frontend && npm run dev

# --- Quality ----------------------------------------------------------------
.PHONY: test
test: ## Run the backend test suite (SQLite)
	cd $(BACKEND) && .venv/bin/python -m pytest

.PHONY: test-pg
test-pg: ## Run the backend test suite against PostgreSQL
	cd $(BACKEND) && TEST_DATABASE_URL="$${TEST_DATABASE_URL:-postgresql+psycopg://inventoryx:devpass@127.0.0.1:55432/inventoryx}" .venv/bin/python -m pytest

.PHONY: cov
cov: ## Test suite with a coverage report
	cd $(BACKEND) && .venv/bin/python -m pytest --cov=src --cov-report=term-missing

.PHONY: lint
lint: ## Lint backend and frontend
	cd $(BACKEND) && .venv/bin/ruff check src tests
	cd Frontend && npm run lint

.PHONY: fmt
fmt: ## Auto-format and auto-fix the backend
	cd $(BACKEND) && .venv/bin/ruff check --fix src tests && .venv/bin/ruff format src tests

# --- Database ---------------------------------------------------------------
.PHONY: migrate
migrate: ## Apply migrations
	cd $(BACKEND) && .venv/bin/alembic upgrade head

.PHONY: migration
migration: ## Create a migration: make migration m="add x"
	cd $(BACKEND) && .venv/bin/alembic revision --autogenerate -m "$(m)"

# --- Docker -----------------------------------------------------------------
.PHONY: up
up: ## Build and start the full stack
	docker compose up -d --build

.PHONY: down
down: ## Stop the stack
	docker compose down

.PHONY: logs
logs: ## Tail stack logs
	docker compose logs -f --tail=100

.PHONY: ps
ps: ## Show stack status
	docker compose ps

.PHONY: backup
backup: ## Dump the database to backups/
	@mkdir -p backups
	docker compose exec -T db pg_dump -U $${POSTGRES_USER:-inventoryx} $${POSTGRES_DB:-inventoryx} \
		| gzip > backups/inventoryx-$$(date +%Y%m%d-%H%M%S).sql.gz
	@echo "Wrote backups/inventoryx-$$(date +%Y%m%d-%H%M%S).sql.gz"
