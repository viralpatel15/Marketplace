.PHONY: help start stop restart build migrate seed logs shell-backend shell-db reset clean test status

# Default target
help:
	@echo ""
	@echo "  YourMarket — Local Dev Commands"
	@echo ""
	@echo "  make start       Start all services"
	@echo "  make stop        Stop all services"
	@echo "  make restart     Restart all services"
	@echo "  make build       Rebuild backend + frontend images"
	@echo "  make migrate     Run Alembic DB migrations"
	@echo "  make seed        Seed subscription plans into DB"
	@echo "  make setup       Full first-time setup (build + migrate + seed + start)"
	@echo "  make logs        Tail logs from all services"
	@echo "  make logs-api    Tail backend API logs only"
	@echo "  make logs-web    Tail frontend logs only"
	@echo "  make status      Show running containers"
	@echo "  make shell-api   Open a shell inside the backend container"
	@echo "  make shell-db    Open a psql shell in the database"
	@echo "  make test        Run backend pytest tests"
	@echo "  make reset       ⚠️  Stop + delete all data (volumes). Fresh start."
	@echo "  make clean       Remove stopped containers and unused images"
	@echo ""

# ── Start / Stop ─────────────────────────────────────────────────────────────

start:
	@echo "Starting all services..."
	docker compose up -d
	@echo ""
	@echo "  Frontend  → http://localhost:3000"
	@echo "  API       → http://localhost:8000"
	@echo "  API Docs  → http://localhost:8000/docs"
	@echo ""

stop:
	@echo "Stopping all services..."
	docker compose down

restart:
	docker compose down
	docker compose up -d

build:
	@echo "Building backend and frontend images..."
	docker compose build backend frontend

# ── Database ──────────────────────────────────────────────────────────────────

migrate:
	@echo "Running Alembic migrations..."
	docker compose run --rm backend alembic upgrade head

seed:
	@echo "Seeding subscription plans..."
	docker compose run --rm backend python seed_plans.py

# ── First-time setup ──────────────────────────────────────────────────────────

setup:
	@echo ""
	@echo "=== First-time setup ==="
	@echo ""
	@[ -f .env ] || (cp .env.example .env && echo "Created .env from .env.example")
	@echo "Starting databases..."
	docker compose up -d postgres redis meilisearch
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 8
	@echo "Building images..."
	docker compose build backend frontend
	@echo "Running migrations..."
	docker compose run --rm backend alembic upgrade head
	@echo "Seeding plans..."
	docker compose run --rm backend python seed_plans.py
	@echo "Starting all services..."
	docker compose up -d
	@echo ""
	@echo "  Setup complete!"
	@echo ""
	@echo "  Frontend  → http://localhost:3000"
	@echo "  API       → http://localhost:8000"
	@echo "  API Docs  → http://localhost:8000/docs"
	@echo ""

# ── Logs ──────────────────────────────────────────────────────────────────────

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f backend

logs-web:
	docker compose logs -f frontend

# ── Status ────────────────────────────────────────────────────────────────────

status:
	@echo ""
	docker compose ps
	@echo ""
	@echo "Health check:"
	@curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "  API not reachable yet"
	@echo ""

# ── Shells ────────────────────────────────────────────────────────────────────

shell-api:
	docker compose exec backend bash

shell-db:
	docker compose exec postgres psql -U admin -d marketplace

# ── Testing ───────────────────────────────────────────────────────────────────

test:
	@echo "Running backend tests..."
	docker compose run --rm backend pytest tests/ -v --tb=short

# ── Admin ─────────────────────────────────────────────────────────────────────

make-admin:
	@read -p "Enter your email to make admin: " email; \
	docker compose exec postgres psql -U admin -d marketplace -c "UPDATE users SET role = 'admin' WHERE email = '$$email'; SELECT id, name, email, role FROM users WHERE email = '$$email';"

# ── Reset / Clean ─────────────────────────────────────────────────────────────

reset:
	@echo ""
	@echo "WARNING: This will delete ALL data (database, search index, uploads)."
	@read -p "Are you sure? Type 'yes' to confirm: " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose down -v; \
		echo "All containers and volumes deleted. Run 'make setup' to start fresh."; \
	else \
		echo "Cancelled."; \
	fi

clean:
	docker compose down
	docker image prune -f
	docker container prune -f
